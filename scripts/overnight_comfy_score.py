#!/usr/bin/env python3
"""Score and report the overnight ComfyUI image/audio run.

Images: CLIP ViT-B/32 prompt-image cosine (same metric as the 2 September
RealVisXL run) plus a blank-image check. Sound effects and music: CLAP
(laion/larger_clap_general) text-audio cosine. Speech: Whisper large-v3-turbo
round trip, word error rate against the input text. Speed: median seconds per
item excluding each session's first item (which includes model load), and
real-time factor for audio.

Writes scores.jsonl, summary.json, REPORT.md and a few downscaled sample
images (samples/) into the run directory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics as st
import textwrap
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DEV = os.environ.get("SCORE_DEVICE", "cuda")

# fp32 runs from before the 22:02 restart, kept as a precision comparison
FP32_REFS = {"z-image-turbo-q8": "z-image-turbo-q8-fp16", "flux1-dev-q8": "flux1-dev-q8-fp16"}

ISSUE_NOTES = {
    "ace-step-1.5-turbo-fp16vae": "First music run (22:02, `--force-fp16`): the audio VAE ran in fp16 and every song came out "
                                  "saturated at full scale. Includes 3 earlier attempts (21:22) that failed because ComfyUI had put the "
                                  "text encoder on the CPU. All discarded; songs were regenerated in fp32.",
    "ace-step-1.5-turbo": "Final fp32 run (`--gpu-only`). The remaining failed attempts are out-of-memory errors in the lyrics/audio-code "
                          "language model; most succeeded once the server was restarted per song, but the songs listed as missing "
                          "ran out of memory even on a fresh server: fp32 ACE-Step 1.5 is at the edge of 16 GB.",
    "vibevoice-1.5b": "The 3 failed attempts were before 22:02: the node requires at least one reference voice. Fixed by building "
                      "two reference voices from the Chatterbox clips; then 45/45.",
    "qwen-image-2512-q4km-lightning4-fp16": "The first image in fp16 was blank (fp16 overflow); the runner switched Qwen-Image to "
                                            "fp32 for the rest of the run.",
}


def precision_of(row: dict) -> str:
    args = row.get("server_args")
    if args is None:
        return "fp32"
    if "--gpu-only" in args:
        return "fp32 (gpu-only)"
    if "--force-fp16" in args:
        return "fp16 + fp32 VAE" if "--fp32-vae" in args else "fp16"
    return "fp32"


MODEL_NOTES = {
    "z-image-turbo-q8": ("Z-Image Turbo 6B", "GGUF Q8_0, Qwen3-4B encoder, 8 steps res_multistep, cfg 1"),
    "flux2-klein-4b": ("FLUX.2 klein 4B", "bf16 safetensors, Qwen3-4B encoder, 4 steps euler, cfg 1"),
    "flux1-schnell-q8": ("FLUX.1 schnell 12B", "GGUF Q8_0, CLIP-L + T5-XXL fp8, 4 steps euler"),
    "flux1-dev-q8": ("FLUX.1 dev 12B", "GGUF Q8_0, CLIP-L + T5-XXL fp8, 20 steps euler, guidance 3.5"),
    "realvisxl-v5": ("RealVisXL V5 (SDXL)", "fp16 checkpoint, 25 steps euler_ancestral, cfg 6.8"),
    "qwen-image-2512-q4km-lightning4": ("Qwen-Image-2512 20B", "GGUF Q4_K_M + Lightning 4-step LoRA, Qwen2.5-VL-7B fp8 encoder, cfg 1"),
    **{k + "-fp16": v for k, v in [
        ("z-image-turbo-q8", ("Z-Image Turbo 6B", "GGUF Q8_0, Qwen3-4B encoder, 8 steps res_multistep, cfg 1")),
        ("flux2-klein-4b", ("FLUX.2 klein 4B", "bf16 safetensors, Qwen3-4B encoder, 4 steps euler, cfg 1")),
        ("flux1-schnell-q8", ("FLUX.1 schnell 12B", "GGUF Q8_0, CLIP-L + T5-XXL fp8, 4 steps euler")),
        ("flux1-dev-q8", ("FLUX.1 dev 12B", "GGUF Q8_0, CLIP-L + T5-XXL fp8, 20 steps euler, guidance 3.5")),
        ("realvisxl-v5", ("RealVisXL V5 (SDXL)", "fp16 checkpoint, 25 steps euler_ancestral, cfg 6.8")),
        ("qwen-image-2512-q4km-lightning4", ("Qwen-Image-2512 20B", "GGUF Q4_K_M + Lightning 4-step LoRA, Qwen2.5-VL-7B fp8 encoder, cfg 1")),
    ]},
    "stable-audio-open-1.0": ("Stable Audio Open 1.0", "T5-base, 50 steps dpmpp_3m_sde, cfg 4.98, 10 s clips"),
    "stable-audio-3-medium": ("Stable Audio 3 Medium", "T5Gemma encoder, 8 steps lcm, cfg 1, 10 s clips, no prompt rewriting"),
    "ace-step-1.5-turbo": ("ACE-Step 1.5 turbo", "all-in-one checkpoint, 8 steps, 60 s songs, fp32 with `--gpu-only`; server restarted per song, so time includes loading the 10 GB checkpoint"),
    "chatterbox": ("Chatterbox", "default voice, exaggeration 0.5, cfg 0.5"),
    "chatterbox-turbo": ("Chatterbox Turbo", "default voice"),
    "vibevoice-1.5b": ("VibeVoice 1.5B", "fp16, 10 diffusion steps, cfg 1.3; reference voices built from the Chatterbox and Chatterbox Turbo clips"),
}


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def load_audio(path: str):
    import soundfile as sf
    import numpy as np
    wav, sr = sf.read(path, dtype="float32", always_2d=True)
    return np.ascontiguousarray(wav.mean(axis=1)), sr


def resample(wav, sr: int, target: int):
    import torch
    import torchaudio.functional as F
    if sr == target:
        return wav
    return F.resample(torch.from_numpy(wav), sr, target).numpy()


def words(s: str) -> list[str]:
    return s.split()


def wer(ref: list[str], hyp: list[str]) -> float:
    if not ref:
        return 0.0 if not hyp else 1.0
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
            prev, d[j] = d[j], cur
    return d[len(hyp)] / len(ref)


class Scorer:
    def __init__(self, run: Path, deadline: float):
        self.run = run
        self.deadline = deadline
        self.path = run / "scores.jsonl"
        self.done = {(r["unit"], r["key"]) for r in read_jsonl(self.path)}

    def out_of_time(self) -> bool:
        return time.time() > self.deadline

    def write(self, row: dict) -> None:
        with self.path.open("a") as fh:
            fh.write(json.dumps(row) + "\n")

    def images(self, rows: list[dict]) -> None:
        import numpy as np
        import torch
        from PIL import Image
        from transformers import CLIPModel, CLIPProcessor
        todo = [r for r in rows if (r["unit"], r["key"]) not in self.done]
        if not todo:
            return
        print(f"CLIP: {len(todo)} images", flush=True)
        proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(DEV).eval()
        for i in range(0, len(todo), 32):
            if self.out_of_time():
                print("CLIP: out of time", flush=True)
                break
            batch = todo[i:i + 32]
            imgs = [Image.open(r["files"][0]).convert("RGB") for r in batch]
            stds = [float(np.asarray(im.resize((256, 256))).std()) for im in imgs]
            with torch.no_grad():
                inp = proc(text=[r["prompt"] for r in batch], images=imgs, return_tensors="pt", padding=True, truncation=True).to(DEV)
                ie = model.get_image_features(pixel_values=inp["pixel_values"])
                te = model.get_text_features(input_ids=inp["input_ids"], attention_mask=inp["attention_mask"])
                ie = getattr(ie, "pooler_output", ie)
                te = getattr(te, "pooler_output", te)
                sims = torch.nn.functional.cosine_similarity(ie, te).tolist()
            for r, s, sd in zip(batch, sims, stds):
                self.write({"unit": r["unit"], "key": r["key"], "clip": round(s, 5), "pixel_std": round(sd, 2), "blank": sd < 4.0})
        del model
        torch.cuda.empty_cache()

    def clap(self, rows: list[dict]) -> None:
        import torch
        from transformers import ClapModel, ClapProcessor
        todo = [r for r in rows if (r["unit"], r["key"]) not in self.done]
        if not todo:
            return
        print(f"CLAP: {len(todo)} clips", flush=True)
        proc = ClapProcessor.from_pretrained("laion/larger_clap_general")
        model = ClapModel.from_pretrained("laion/larger_clap_general").to(DEV).eval()
        for r in todo:
            if self.out_of_time():
                print("CLAP: out of time", flush=True)
                break
            try:
                wav, sr = load_audio(r["files"][0])
                dur = len(wav) / sr
                rms = float((wav ** 2).mean() ** 0.5)
                w48 = resample(wav, sr, 48000)
                with torch.no_grad():
                    try:
                        inp = proc(text=[r["prompt"]], audio=[w48], sampling_rate=48000, return_tensors="pt", padding=True)
                    except TypeError:
                        inp = proc(text=[r["prompt"]], audios=[w48], sampling_rate=48000, return_tensors="pt", padding=True)
                    inp = {k: v.to(DEV) for k, v in inp.items()}
                    out = model(**inp)
                    s = torch.nn.functional.cosine_similarity(out.text_embeds, out.audio_embeds).item()
                self.write({"unit": r["unit"], "key": r["key"], "clap": round(s, 5), "audio_s": round(dur, 2),
                            "rms": round(rms, 5), "silent": rms < 1e-3})
            except Exception as e:
                self.write({"unit": r["unit"], "key": r["key"], "error": f"clap: {e}"[:300]})
        del model
        torch.cuda.empty_cache()

    def asr(self, rows: list[dict]) -> None:
        import torch
        from transformers import pipeline
        todo = [r for r in rows if (r["unit"], r["key"]) not in self.done]
        if not todo:
            return
        print(f"Whisper: {len(todo)} clips", flush=True)
        asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3-turbo",
                       torch_dtype=torch.float16 if DEV == "cuda" else torch.float32, device=DEV)
        norm = asr.tokenizer.normalize if hasattr(asr.tokenizer, "normalize") else (lambda s: re.sub(r"[^\w\s']", " ", s.lower()))
        for r in todo:
            if self.out_of_time():
                print("Whisper: out of time", flush=True)
                break
            try:
                wav, sr = load_audio(r["files"][0])
                dur = len(wav) / sr
                w16 = resample(wav, sr, 16000)
                hyp = asr({"raw": w16, "sampling_rate": 16000}, chunk_length_s=30, batch_size=4,
                          generate_kwargs={"language": "en", "task": "transcribe"})["text"]
                ref = re.sub(r"\[\d\]\s*", " ", r.get("text") or r["prompt"])
                e = wer(words(norm(ref)), words(norm(hyp)))
                self.write({"unit": r["unit"], "key": r["key"], "wer": round(e, 4), "audio_s": round(dur, 2),
                            "hyp": hyp.strip()[:500]})
            except Exception as e:
                self.write({"unit": r["unit"], "key": r["key"], "error": f"asr: {e}"[:300]})
        del asr
        torch.cuda.empty_cache()


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 4) if xs else None


def median(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 2) if xs else None


def load_results(run: Path) -> list[dict]:
    """results.jsonl. The ACE-Step rows from the 22:02 session (keyed by musical key,
    e.g. "D minor") ran with an fp16 audio VAE and are saturated noise; they are moved
    to a separate unit that is reported as a failure and not scored."""
    rows = read_jsonl(run / "results.jsonl")
    for r in rows:
        if r.get("unit") == "ace-step-1.5-turbo" and r.get("key") != "__unit__" and not str(r.get("key", "")).startswith("music_"):
            r["unit"] = "ace-step-1.5-turbo-fp16vae"
            r["kind"] = "broken"
            r["key"] = f"music_{r['idx']:02d}"
            r["status"] = "error"
            r["error"] = "fp16 audio VAE: output saturated at full scale (all samples ±1)"
    return rows


def summarize(run: Path) -> dict:
    res = load_results(run)
    scores = {}
    for s in read_jsonl(run / "scores.jsonl"):
        scores.setdefault((s["unit"], s["key"]), {}).update(s)
    latest = {}
    unit_end = {}
    attempts = defaultdict(lambda: {"ok": 0, "err": 0, "errors": [], "failed_keys": set()})
    for r in res:
        if r.get("status") == "unit_end":
            unit_end[r["unit"]] = r
            continue
        a = attempts[r["unit"]]
        if r["status"] == "success":
            a["ok"] += 1
            latest[(r["unit"], r["key"])] = r
        else:
            a["err"] += 1
            a["failed_keys"].add(r["key"])
            first = (r.get("error") or "").strip().splitlines()[0][:200] if r.get("error") else ""
            if first and first not in a["errors"] and len(a["errors"]) < 3:
                a["errors"].append(first)

    units = {}
    for (u, k), r in latest.items():
        units.setdefault(u, {"kind": r["kind"], "rows": []})["rows"].append({**r, **scores.get((u, k), {})})

    # common GenEval prefix: prompts every image model completed
    img_units = [u for u, d in units.items() if d["kind"] == "image" and u not in FP32_REFS]
    common = None
    for u in img_units:
        keys = {r["key"] for r in units[u]["rows"]}
        common = keys if common is None else common & keys
    common = common or set()

    out = {"generated": datetime.now().isoformat(timespec="seconds"), "common_image_prompts": len(common), "units": {}}
    for u, d in units.items():
        rows = d["rows"]
        warm = [r["wall_s"] for r in rows if not r.get("first_of_session")]
        first = [r["wall_s"] for r in rows if r.get("first_of_session")]
        s = {"kind": d["kind"], "n": len(rows), "failed_attempts": attempts[u]["err"], "errors": attempts[u]["errors"],
             "precision": ", ".join(sorted({precision_of(r) for r in rows})),
             "missing": sorted(attempts[u]["failed_keys"] - {r["key"] for r in rows}),
             "median_s": median(warm), "first_item_s": median(first), "stop_reason": unit_end.get(u, {}).get("reason"),
             "minutes": unit_end.get(u, {}).get("minutes")}
        if d["kind"] == "image":
            s["clip_mean"] = mean([r.get("clip") for r in rows])
            s["clip_common"] = mean([r.get("clip") for r in rows if r["key"] in common])
            s["blank"] = sum(1 for r in rows if r.get("blank"))
            s["images_per_min"] = round(60 / s["median_s"], 2) if s["median_s"] else None
            by_tag = defaultdict(list)
            for r in rows:
                if r["key"] in common:
                    by_tag[r["tag"]].append(r.get("clip"))
            s["clip_by_tag_common"] = {t: mean(v) for t, v in sorted(by_tag.items())}
        else:
            audio_s = [r.get("audio_s") for r in rows if r.get("audio_s")]
            rtf = [r["wall_s"] / r["audio_s"] for r in rows if r.get("audio_s") and not r.get("first_of_session")]
            s["audio_s_mean"] = mean(audio_s)
            s["rtf_median"] = round(st.median(rtf), 3) if rtf else None
            if d["kind"] in ("sfx", "music"):
                s["clap_mean"] = mean([r.get("clap") for r in rows])
                s["silent"] = sum(1 for r in rows if r.get("silent"))
                if d["kind"] == "music":
                    s["clap_instrumental"] = mean([r.get("clap") for r in rows if r.get("tag") == "instrumental"])
                    s["clap_vocal"] = mean([r.get("clap") for r in rows if r.get("tag") == "vocal"])
            else:
                s["wer_mean"] = mean([r.get("wer") for r in rows])
                s["wer_median"] = median([r.get("wer") for r in rows])
                s["wer_sentences"] = mean([r.get("wer") for r in rows if r.get("tag") == "sentence"])
                s["wer_dialogs"] = mean([r.get("wer") for r in rows if r.get("tag") == "dialog"])
        out["units"][u] = s
    # units that never produced anything
    for u, a in attempts.items():
        if u not in out["units"]:
            out["units"][u] = {"kind": "?", "n": 0, "failed_attempts": a["err"], "errors": a["errors"], "missing": [],
                               "stop_reason": unit_end.get(u, {}).get("reason")}
    ab = {}
    for ref, main in FP32_REFS.items():
        if ref in units and main in units:
            a = {r["key"]: r for r in units[ref]["rows"]}
            b = {r["key"]: r for r in units[main]["rows"]}
            shared = sorted(set(a) & set(b))
            if shared:
                ab[ref] = {"fp16_unit": main, "shared": len(shared),
                           "fp32_median_s": median([a[k]["wall_s"] for k in shared if not a[k].get("first_of_session")]),
                           "fp16_median_s": median([b[k]["wall_s"] for k in shared if not b[k].get("first_of_session")]),
                           "fp32_clip": mean([a[k].get("clip") for k in shared]),
                           "fp16_clip": mean([b[k].get("clip") for k in shared])}
    out["fp32_vs_fp16"] = ab
    out["_common_keys"] = sorted(common)
    return out


def fmt(x, nd=3):
    return "—" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def gpu_stats(run: Path) -> str:
    p = run / "logs" / "gpu.csv"
    if not p.exists():
        return ""
    per = defaultdict(lambda: {"t": [], "p": []})
    for line in p.read_text().splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 7:
            continue
        try:
            per[parts[1]]["t"].append(float(parts[2]))
            per[parts[1]]["p"].append(float(parts[3]))
        except ValueError:
            pass
    return "; ".join(f"GPU {g}: max {max(v['t']):.0f} °C, mean {sum(v['p']) / len(v['p']):.0f} W"
                     for g, v in sorted(per.items()) if v["t"])


def report(run: Path, summ: dict) -> str:
    U = summ["units"]
    L = ["# Overnight ComfyUI text-to-image and text-to-audio test", "",
         f"Two Tesla P100-PCIE-16GB, ComfyUI 0.35.0, PyTorch 2.14.1+cu126, one ComfyUI server per GPU. "
         f"Run 7–8 October 2026, report generated {summ['generated']}.", "",
         "Prompts are processed in a fixed order, so a model that ran out of time budget still has a prefix "
         "that compares directly with the others. Speed is the median per item after the first (the first "
         "includes model load). Each image is 1024×1024 with one seed per prompt (seed = 1000 + index). "
         "The Precision column shows what each model actually ran in (see the fp32 vs fp16 section).", ""]
    gs = gpu_stats(run)
    if gs:
        L += [f"GPU telemetry: {gs}.", ""]

    img = {u: s for u, s in U.items() if s.get("kind") == "image" and u not in FP32_REFS}
    if img:
        L += ["## Text → image (GenEval prompts, CLIP ViT-B/32)", "",
              "![Same prompts and seeds across models](samples/grid.jpg)", "",
              "*`samples/grid.jpg`: one row per model, the same six prompts across. Judge quality from the images; "
              "CLIP mostly tells you whether the objects are there.*", "",
              f"`CLIP common` averages over the {summ['common_image_prompts']} prompts every image model completed. "
              "CLIP cosine is a coarse prompt-alignment signal; it does not measure image quality.", "",
              "| Model | Setup | Precision | Images | s / image | Images / min | CLIP common | CLIP all | Blank | Stop |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
        for u, s in sorted(img.items(), key=lambda kv: -(kv[1].get("clip_common") or 0)):
            name, setup = MODEL_NOTES.get(u, (u, ""))
            L.append(f"| {name} | {setup} | {s.get('precision', '')} | {s['n']} | {fmt(s.get('median_s'), 1)} | {fmt(s.get('images_per_min'), 2)} | "
                     f"{fmt(s.get('clip_common'))} | {fmt(s.get('clip_mean'))} | {s.get('blank', 0)} | {s.get('stop_reason') or '—'} |")
        tags = sorted({t for s in img.values() for t in (s.get("clip_by_tag_common") or {})})
        if tags:
            L += ["", "CLIP by GenEval category (common prompts):", "",
                  "| Model | " + " | ".join(tags) + " |", "|---|" + "---:|" * len(tags)]
            for u, s in img.items():
                L.append(f"| {MODEL_NOTES.get(u, (u,))[0]} | " + " | ".join(fmt((s.get('clip_by_tag_common') or {}).get(t)) for t in tags) + " |")
        L.append("")

    ab = summ.get("fp32_vs_fp16") or {}
    if ab:
        L += ["### fp32 vs fp16 on the P100", "",
              "ComfyUI keeps Pascal cards in fp32 on Linux. The run started that way; at 22:02 it was restarted with "
              "`--force-fp16`, which ACE-Step needs (it moves text encoders onto the GPU). The fp32 images made before the "
              "restart are compared here with the fp16 images for the same prompts and seeds.", "",
              "| Model | Shared prompts | fp32 s / image | fp16 s / image | fp32 CLIP | fp16 CLIP |", "|---|---:|---:|---:|---:|---:|"]
        for ref, d in ab.items():
            L.append(f"| {MODEL_NOTES.get(ref, (ref,))[0]} | {d['shared']} | {fmt(d['fp32_median_s'], 1)} | {fmt(d['fp16_median_s'], 1)} | "
                     f"{fmt(d['fp32_clip'])} | {fmt(d['fp16_clip'])} |")
        L.append("")
    sfx = {u: s for u, s in U.items() if s.get("kind") == "sfx"}
    if sfx:
        L += ["## Text → sound effects (AudioCaps test captions, CLAP)", "",
              "| Model | Setup | Precision | Clips | s / clip | RTF | CLAP | Silent | Stop |", "|---|---|---|---:|---:|---:|---:|---:|---|"]
        for u, s in sfx.items():
            name, setup = MODEL_NOTES.get(u, (u, ""))
            L.append(f"| {name} | {setup} | {s.get('precision', '')} | {s['n']} | {fmt(s.get('median_s'), 1)} | {fmt(s.get('rtf_median'), 2)} | "
                     f"{fmt(s.get('clap_mean'))} | {s.get('silent', 0)} | {s.get('stop_reason') or '—'} |")
        L.append("")
    mus = {u: s for u, s in U.items() if s.get("kind") == "music"}
    if mus:
        L += ["## Text → music (20 prompts, 10 instrumental + 10 with lyrics, CLAP vs. style tags)", "",
              "| Model | Setup | Songs | s / song | RTF | CLAP all | CLAP instr. | CLAP vocal | Stop |",
              "|---|---|---:|---:|---:|---:|---:|---:|---|"]
        for u, s in mus.items():
            name, setup = MODEL_NOTES.get(u, (u, ""))
            L.append(f"| {name} | {setup} | {s['n']} | {fmt(s.get('median_s'), 1)} | {fmt(s.get('rtf_median'), 2)} | "
                     f"{fmt(s.get('clap_mean'))} | {fmt(s.get('clap_instrumental'))} | {fmt(s.get('clap_vocal'))} | {s.get('stop_reason') or '—'} |")
        L.append("")
    tts = {u: s for u, s in U.items() if s.get("kind") == "tts"}
    if tts:
        L += ["## Text → speech (40 sentences; VibeVoice also 5 two-speaker dialogues; Whisper large-v3-turbo WER)", "",
              "| Model | Setup | Precision | Clips | s / clip | RTF | WER mean | WER median | WER dialogs | Stop |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
        for u, s in tts.items():
            name, setup = MODEL_NOTES.get(u, (u, ""))
            L.append(f"| {name} | {setup} | {s.get('precision', '')} | {s['n']} | {fmt(s.get('median_s'), 1)} | {fmt(s.get('rtf_median'), 2)} | "
                     f"{fmt(s.get('wer_sentences') if s.get('wer_sentences') is not None else s.get('wer_mean'))} | {fmt(s.get('wer_median'))} | "
                     f"{fmt(s.get('wer_dialogs'))} | {s.get('stop_reason') or '—'} |")
        L.append("")
    L += ["RTF = generation seconds per second of audio (below 1 is faster than real time).", ""]

    probs = {u: s for u, s in U.items() if s.get("failed_attempts") or s.get("n", 0) == 0}
    if probs:
        L += ["## Problems during the night", ""]
        for u, s in probs.items():
            line = f"- **{u}**: {s.get('n', 0)} succeeded, {s.get('failed_attempts', 0)} failed attempts."
            if s.get("missing"):
                line += f" Never succeeded: {', '.join(s['missing'])}."
            if u in ISSUE_NOTES:
                line += " " + ISSUE_NOTES[u]
            if s.get("errors"):
                line += " Errors: " + "; ".join(f"`{e}`" for e in s["errors"])
            L.append(line)
        L.append("")
    L += ["## Files", "",
          f"- Generated images and audio: `{run}/out/gpu*/<model>/`",
          "- Per-item results: `results.jsonl`; scores: `scores.jsonl`; summary: `summary.json`; logs: `logs/`; side-by-side samples: `samples/`",
          "- Runner, scorer and prompts: `~/Projects/Tests/scripts/overnight_comfy_{av,score}.py`, `overnight_comfy_prompts.json`", ""]
    return "\n".join(L)


def make_grid(run: Path, summ: dict, cols: int = 6, cell: int = 256) -> None:
    from PIL import Image, ImageDraw
    keys = summ.get("_common_keys", [])
    if not keys:
        return
    step = max(1, len(keys) // cols)
    keys = keys[::step][:cols]
    files = {}
    for r in load_results(run):
        if r.get("status") == "success" and r.get("kind") == "image" and r["key"] in keys and r["unit"] not in FP32_REFS:
            files[(r["unit"], r["key"])] = r["files"][0]
    units = sorted({u for u, _ in files})
    label_w, top = 190, 60
    prompts = {r["key"]: r["prompt"] for r in load_results(run) if r.get("kind") == "image" and r.get("prompt")}
    grid = Image.new("RGB", (label_w + cols * cell, top + len(units) * cell), "white")
    d = ImageDraw.Draw(grid)
    for j, k in enumerate(keys):
        d.text((label_w + j * cell + 6, 6), "\n".join(textwrap.wrap(prompts.get(k, k), 34)[:3]), fill="black")
    for i, u in enumerate(units):
        d.text((6, top + i * cell + cell // 2 - 8), MODEL_NOTES.get(u, (u,))[0], fill="black")
        for j, k in enumerate(keys):
            f = files.get((u, k))
            if f:
                grid.paste(Image.open(f).convert("RGB").resize((cell, cell)), (label_w + j * cell, top + i * cell))
    (run / "samples").mkdir(exist_ok=True)
    grid.save(run / "samples" / "grid.jpg", quality=88)


def make_samples(run: Path, summ: dict) -> None:
    """Four shared prompts per image model as small JPEGs, for side-by-side viewing."""
    from PIL import Image
    keys = summ.get("_common_keys", [])[:4]
    gal = run / "samples"
    gal.mkdir(exist_ok=True)
    for r in read_jsonl(run / "results.jsonl"):
        if r.get("status") == "success" and r.get("kind") == "image" and r["key"] in keys:
            try:
                Image.open(r["files"][0]).convert("RGB").resize((384, 384)).save(gal / f"{r['unit']}__{r['key']}.jpg", quality=85)
            except Exception:
                pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--deadline", default="2026-10-08T05:45")
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    run = a.run_dir
    deadline = datetime.fromisoformat(a.deadline).timestamp()

    if not a.report_only:
        res = load_results(run)
        latest = {}
        for r in res:
            if r.get("status") == "success":
                latest[(r["unit"], r["key"])] = r
        rows = list(latest.values())
        sc = Scorer(run, deadline)
        for kind, fn in [("tts", sc.asr), ("sfx", sc.clap), ("music", sc.clap), ("image", sc.images)]:
            try:
                fn([r for r in rows if r["kind"] == kind])
            except Exception as e:
                print(f"scoring {kind} failed: {e!r}", flush=True)
    summ = summarize(run)
    (run / "summary.json").write_text(json.dumps({k: v for k, v in summ.items() if k != "_common_keys"}, indent=2))
    (run / "REPORT.md").write_text(report(run, summ))
    make_samples(run, summ)
    make_grid(run, summ)
    print(f"report: {run / 'REPORT.md'}", flush=True)


if __name__ == "__main__":
    main()

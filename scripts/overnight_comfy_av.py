#!/usr/bin/env python3
"""Overnight ComfyUI text-to-image and text-to-audio benchmark on the two P100s.

Starts one ComfyUI server per GPU (cu126 venv), then two workers pull model
"units" from a shared queue. Each unit has a time budget and a fixed prompt
order, so a unit that runs out of time still leaves a prefix that is directly
comparable with the other models. No new item starts after --gen-deadline;
afterwards the servers are stopped and scoring (overnight_comfy_score.py) runs.

Resumable: items already recorded as successful in results.jsonl are skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

COMFY = Path("/home/hm/AI/ComfyUI")
PY = COMFY / ".venv-cu126" / "bin" / "python"
TESTS = Path.home() / "Projects" / "Tests"
GENEVAL = TESTS / "tools" / "geneval" / "prompts" / "evaluation_metadata.jsonl"
AUDIOCAPS = TESTS / "datasets" / "audiocaps" / "data" / "test-00000-of-00001-069405200b9b7a9f.parquet"
HERE = Path(__file__).resolve().parent
PROMPTS = HERE / "overnight_comfy_prompts.json"

MIN_FREE_GB = 2.0
LOCK = threading.Lock()
STOP = threading.Event()


def now() -> float:
    return time.time()


def stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


class Log:
    def __init__(self, path: Path):
        self.path = path

    def __call__(self, *parts: Any) -> None:
        line = f"[{stamp()}] " + " ".join(str(p) for p in parts)
        with LOCK:
            print(line, flush=True)
            with self.path.open("a") as fh:
                fh.write(line + "\n")


# --------------------------------------------------------------------------- server

class Server:
    def __init__(self, gpu: int, run: Path, log: Log, extra: list[str] | None = None):
        self.gpu = gpu
        self.port = 8190 + gpu
        self.url = f"http://127.0.0.1:{self.port}"
        self.out = run / "out" / f"gpu{gpu}"
        self.user = run / "comfy_user" / f"gpu{gpu}"
        self.logfile = run / "logs" / f"comfy_gpu{gpu}.log"
        self.log = log
        self.extra = extra or []
        self.proc: subprocess.Popen | None = None

    def start(self) -> None:
        self.out.mkdir(parents=True, exist_ok=True)
        self.user.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(self.gpu), PYTHONUNBUFFERED="1")
        cmd = [str(PY), "main.py", "--listen", "127.0.0.1", "--port", str(self.port),
               "--output-directory", str(self.out), "--user-directory", str(self.user),
               "--disable-auto-launch", "--disable-api-nodes", *self.extra]
        fh = self.logfile.open("a")
        fh.write(f"\n==== start {datetime.now().isoformat()} {' '.join(cmd)}\n")
        fh.flush()
        self.proc = subprocess.Popen(cmd, cwd=COMFY, env=env, stdout=fh, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, start_new_session=True)
        for _ in range(240):
            if self.alive() and self.up():
                self.log(f"gpu{self.gpu}: server up on :{self.port}")
                return
            if not self.alive():
                break
            time.sleep(1)
        raise RuntimeError(f"gpu{self.gpu}: ComfyUI did not start, see {self.logfile}")

    def alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def up(self) -> bool:
        try:
            self.get("/system_stats", timeout=3)
            return True
        except Exception:
            return False

    def stop(self) -> None:
        if not self.proc:
            return
        try:
            os.killpg(self.proc.pid, signal.SIGTERM)
            self.proc.wait(timeout=30)
        except Exception:
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)
            except Exception:
                pass
        self.proc = None

    def ensure_args(self, args: list[str]) -> None:
        """(Re)start the server if it is not running with these launch flags."""
        if args != self.extra or not self.alive():
            self.log(f"gpu{self.gpu}: server flags {self.extra} -> {args}")
            self.stop()
            time.sleep(3)
            self.extra = list(args)
            self.start()

    def restart(self) -> None:
        self.log(f"gpu{self.gpu}: restarting server")
        self.stop()
        time.sleep(5)
        self.start()

    def get(self, ep: str, timeout: float = 30) -> Any:
        with urllib.request.urlopen(self.url + ep, timeout=timeout) as r:
            return json.loads(r.read() or b"null")

    def post(self, ep: str, payload: dict, timeout: float = 30) -> Any:
        req = urllib.request.Request(self.url + ep, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                return json.loads(body) if body else None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:2000]}") from None

    def free(self) -> None:
        try:
            self.post("/free", {"unload_models": True, "free_memory": True})
            time.sleep(3)
        except Exception as e:
            self.log(f"gpu{self.gpu}: /free failed: {e}")

    def run(self, workflow: dict, timeout: float) -> dict:
        """Queue one workflow and wait. Returns {'ok', 'files', 'error'}."""
        resp = self.post("/prompt", {"prompt": workflow, "client_id": f"bench-{self.gpu}"})
        pid = resp["prompt_id"]
        t_end = now() + timeout
        while now() < t_end:
            if not self.alive():
                return {"ok": False, "files": [], "error": "server died", "fatal": True}
            try:
                hist = self.get(f"/history/{pid}", timeout=10)
            except Exception:
                hist = None
            if hist and pid in hist:
                h = hist[pid]
                status = h.get("status", {})
                files: list[str] = []
                for out in h.get("outputs", {}).values():
                    for key in ("images", "audio"):
                        for f in out.get(key, []) or []:
                            if f.get("type") == "output":
                                files.append(str(self.out / f.get("subfolder", "") / f["filename"]))
                if status.get("status_str") == "success" and files:
                    return {"ok": True, "files": files, "error": None}
                err = None
                for kind, msg in status.get("messages", []):
                    if kind == "execution_error":
                        err = f"{msg.get('node_type')}: {msg.get('exception_type')}: {msg.get('exception_message', '')[:600]}"
                if status.get("completed") or status.get("status_str") == "error":
                    return {"ok": False, "files": files, "error": err or f"no output ({status.get('status_str')})"}
            time.sleep(0.5)
        try:
            self.post("/interrupt", {})
            self.post("/queue", {"clear": True})
        except Exception:
            pass
        time.sleep(5)
        return {"ok": False, "files": [], "error": f"timeout after {timeout:.0f}s"}


def is_blank(path: str) -> bool:
    try:
        import numpy as np
        from PIL import Image
        return float(np.asarray(Image.open(path).convert("RGB").resize((256, 256))).std()) < 4.0
    except Exception:
        return False


def bad_audio(path: str) -> str | None:
    try:
        import numpy as np
        import soundfile as sf
        w, _ = sf.read(path, always_2d=True)
        if np.isnan(w).any():
            return "audio contains NaN"
        if (np.abs(w) >= 0.999).mean() > 0.2:
            return "saturated audio (likely fp16 overflow)"
        if float(np.sqrt((w ** 2).mean())) < 1e-4:
            return "silent audio"
    except Exception as e:
        return f"unreadable audio: {e}"
    return None


# --------------------------------------------------------------------------- workflows

def N(cls: str, **inputs: Any) -> dict:
    return {"class_type": cls, "inputs": inputs}


def save_image(prefix: str, src: str) -> dict:
    return N("SaveImage", images=[src, 0], filename_prefix=prefix)


def wf_zimage(p: str, seed: int, prefix: str, v: dict) -> dict:
    return {
        "1": N("UnetLoaderGGUF", unet_name="z-image-turbo-Q8_0.gguf"),
        "2": N("ModelSamplingAuraFlow", model=["1", 0], shift=3.0),
        "3": N("CLIPLoader", clip_name="qwen_3_4b.safetensors", type="lumina2"),
        "4": N("CLIPTextEncode", clip=["3", 0], text=p),
        "5": N("ConditioningZeroOut", conditioning=["4", 0]),
        "6": N("EmptySD3LatentImage", width=1024, height=1024, batch_size=1),
        "7": N("KSampler", model=["2", 0], seed=seed, steps=8, cfg=1.0, sampler_name="res_multistep",
               scheduler="simple", positive=["4", 0], negative=["5", 0], latent_image=["6", 0], denoise=1.0),
        "8": N("VAELoader", vae_name="ae.safetensors"),
        "9": N("VAEDecode", samples=["7", 0], vae=["8", 0]),
        "10": save_image(prefix, "9"),
    }


def wf_klein(p: str, seed: int, prefix: str, v: dict) -> dict:
    return {
        "1": N("UNETLoader", unet_name="flux-2-klein-4b.safetensors", weight_dtype="default"),
        "3": N("CLIPLoader", clip_name="qwen_3_4b.safetensors", type="flux2"),
        "4": N("CLIPTextEncode", clip=["3", 0], text=p),
        "5": N("ConditioningZeroOut", conditioning=["4", 0]),
        "6": N("EmptyFlux2LatentImage", width=1024, height=1024, batch_size=1),
        "11": N("CFGGuider", model=["1", 0], positive=["4", 0], negative=["5", 0], cfg=1.0),
        "12": N("KSamplerSelect", sampler_name="euler"),
        "13": N("Flux2Scheduler", steps=4, width=1024, height=1024),
        "14": N("RandomNoise", noise_seed=seed),
        "7": N("SamplerCustomAdvanced", noise=["14", 0], guider=["11", 0], sampler=["12", 0],
               sigmas=["13", 0], latent_image=["6", 0]),
        "8": N("VAELoader", vae_name="flux2-vae.safetensors"),
        "9": N("VAEDecode", samples=["7", 0], vae=["8", 0]),
        "10": save_image(prefix, "9"),
    }


def wf_flux1(unet: str, steps: int, guidance: float | None) -> Callable:
    def build(p: str, seed: int, prefix: str, v: dict) -> dict:
        wf = {
            "1": N("UnetLoaderGGUF", unet_name=unet),
            "3": N("DualCLIPLoader", clip_name1="clip_l.safetensors",
                   clip_name2="t5xxl_fp8_e4m3fn_scaled.safetensors", type="flux"),
            "4": N("CLIPTextEncode", clip=["3", 0], text=p),
            "5": N("ConditioningZeroOut", conditioning=["4", 0]),
            "6": N("EmptySD3LatentImage", width=1024, height=1024, batch_size=1),
            "8": N("VAELoader", vae_name="ae.safetensors"),
        }
        pos = ["4", 0]
        if guidance is not None:
            wf["15"] = N("FluxGuidance", conditioning=["4", 0], guidance=guidance)
            pos = ["15", 0]
        wf["7"] = N("KSampler", model=["1", 0], seed=seed, steps=steps, cfg=1.0, sampler_name="euler",
                    scheduler="simple", positive=pos, negative=["5", 0], latent_image=["6", 0], denoise=1.0)
        wf["9"] = N("VAEDecode", samples=["7", 0], vae=["8", 0])
        wf["10"] = save_image(prefix, "9")
        return wf
    return build


def wf_qwen(p: str, seed: int, prefix: str, v: dict) -> dict:
    return {
        "1": N("UnetLoaderGGUF", unet_name="qwen-image-2512-Q4_K_M.gguf"),
        "16": N("LoraLoaderModelOnly", model=["1", 0],
                lora_name="Qwen-Image-2512-Lightning-4steps-V1.0-bf16.safetensors", strength_model=1.0),
        "2": N("ModelSamplingAuraFlow", model=["16", 0], shift=3.1),
        "3": N("CLIPLoader", clip_name="qwen_2.5_vl_7b_fp8_scaled.safetensors", type="qwen_image"),
        "4": N("CLIPTextEncode", clip=["3", 0], text=p),
        "5": N("ConditioningZeroOut", conditioning=["4", 0]),
        "6": N("EmptySD3LatentImage", width=1024, height=1024, batch_size=1),
        "7": N("KSampler", model=["2", 0], seed=seed, steps=4, cfg=1.0, sampler_name="euler",
               scheduler="simple", positive=["4", 0], negative=["5", 0], latent_image=["6", 0], denoise=1.0),
        "8": N("VAELoader", vae_name="qwen_image_vae.safetensors"),
        "9": N("VAEDecode", samples=["7", 0], vae=["8", 0]),
        "10": save_image(prefix, "9"),
    }


def wf_realvis(p: str, seed: int, prefix: str, v: dict) -> dict:
    return {
        "1": N("CheckpointLoaderSimple", ckpt_name="RealVisXL_V5.0_fp16.safetensors"),
        "4": N("CLIPTextEncode", clip=["1", 1], text=p),
        "5": N("CLIPTextEncode", clip=["1", 1], text=""),
        "6": N("EmptyLatentImage", width=1024, height=1024, batch_size=1),
        "7": N("KSampler", model=["1", 0], seed=seed, steps=25, cfg=6.8, sampler_name="euler_ancestral",
               scheduler="normal", positive=["4", 0], negative=["5", 0], latent_image=["6", 0], denoise=1.0),
        "9": N("VAEDecode", samples=["7", 0], vae=["1", 2]),
        "10": save_image(prefix, "9"),
    }


def save_audio(prefix: str, src: list) -> dict:
    return N("SaveAudio", audio=src, filename_prefix=prefix)


def wf_sao(p: str, seed: int, prefix: str, v: dict) -> dict:
    secs = 10.0
    return {
        "1": N("CheckpointLoaderSimple", ckpt_name="stable-audio-open-1.0.safetensors"),
        "3": N("CLIPLoader", clip_name="t5_base.safetensors", type="stable_audio"),
        "4": N("CLIPTextEncode", clip=["3", 0], text=p),
        "5": N("CLIPTextEncode", clip=["3", 0], text=""),
        "11": N("ConditioningStableAudio", positive=["4", 0], negative=["5", 0], seconds_start=0.0, seconds_total=secs),
        "6": N("EmptyLatentAudio", seconds=secs, batch_size=1),
        "7": N("KSampler", model=["1", 0], seed=seed, steps=50, cfg=4.98, sampler_name="dpmpp_3m_sde_gpu",
               scheduler="exponential", positive=["11", 0], negative=["11", 1], latent_image=["6", 0], denoise=1.0),
        "9": N("VAEDecodeAudio", samples=["7", 0], vae=["1", 2]),
        "10": save_audio(prefix, ["9", 0]),
    }


def wf_sa3(p: str, seed: int, prefix: str, v: dict) -> dict:
    secs = 10.0
    return {
        "1": N("CheckpointLoaderSimple", ckpt_name="stable_audio_3_medium.safetensors"),
        "3": N("CLIPLoader", clip_name="t5gemma_b_b_ul2.safetensors", type="stable_audio"),
        "4": N("CLIPTextEncode", clip=["3", 0], text=p),
        "5": N("CLIPTextEncode", clip=["3", 0], text=""),
        "6": N("EmptyLatentAudio", seconds=secs, batch_size=1),
        "7": N("KSampler", model=["1", 0], seed=seed, steps=8, cfg=1.0, sampler_name="lcm",
               scheduler="simple", positive=["4", 0], negative=["5", 0], latent_image=["6", 0], denoise=1.0),
        "9": N("VAEDecodeAudio", samples=["7", 0], vae=["1", 2]),
        "10": save_audio(prefix, ["9", 0]),
    }


def wf_ace15(item: dict, seed: int, prefix: str, v: dict) -> dict:
    secs = float(item["seconds"])
    return {
        "1": N("CheckpointLoaderSimple", ckpt_name="ace_step_1.5_turbo_aio.safetensors"),
        "4": N("TextEncodeAceStepAudio1.5", clip=["1", 1], tags=item["tags"], lyrics=item["lyrics"], seed=seed,
               bpm=int(item["bpm"]), duration=secs, timesignature="4", language="en", keyscale=item["keyscale"],
               generate_audio_codes=True, cfg_scale=2.0, temperature=0.85, top_p=0.9, top_k=0, min_p=0.0),
        "5": N("ConditioningZeroOut", conditioning=["4", 0]),
        "2": N("ModelSamplingAuraFlow", model=["1", 0], shift=3.0),
        "6": N("EmptyAceStep1.5LatentAudio", seconds=secs, batch_size=1),
        "7": N("KSampler", model=["2", 0], seed=seed, steps=8, cfg=1.0, sampler_name="euler",
               scheduler="simple", positive=["4", 0], negative=["5", 0], latent_image=["6", 0], denoise=1.0),
        "9": N("VAEDecodeAudio", samples=["7", 0], vae=["1", 2]),
        "10": save_audio(prefix, ["9", 0]),
    }


def wf_chatterbox(text: str, seed: int, prefix: str, v: dict) -> dict:
    return {
        "1": N("FL_ChatterboxTTS", text=text, exaggeration=0.5, cfg_weight=0.5, temperature=0.8, seed=seed,
               use_cpu=False, keep_model_loaded=True),
        "10": save_audio(prefix, ["1", 0]),
    }


def wf_chatterbox_turbo(text: str, seed: int, prefix: str, v: dict) -> dict:
    return {
        "1": N("FL_ChatterboxTurboTTS", text=text, temperature=0.8, top_k=1000, top_p=0.95,
               repetition_penalty=1.2, seed=seed, use_cpu=False, keep_model_loaded=True),
        "10": save_audio(prefix, ["1", 0]),
    }


def wf_vibevoice(text: str, seed: int, prefix: str, v: dict) -> dict:
    return {
        "1": N("VibeVoiceTTS", model_name="VibeVoice-1.5B", text=text, quantize_llm_4bit=False,
               attention_mode="sdpa", cfg_scale=1.3, inference_steps=10, seed=seed, do_sample=True,
               temperature=0.95, top_p=0.95, top_k=0, max_new_tokens=0, force_offload=False,
               device="cuda", dtype=v.get("dtype", "fp16"), voice_preset="None",
               speaker_1_voice=["2", 0], speaker_2_voice=["3", 0]),
        "2": N("LoadAudio", audio="vv_ref_1.flac"),
        "3": N("LoadAudio", audio="vv_ref_2.flac"),
        "10": save_audio(prefix, ["1", 0]),
    }


# --------------------------------------------------------------------------- prompt sets

def geneval_items() -> list[dict]:
    rows = [json.loads(l) for l in GENEVAL.read_text().splitlines() if l.strip()]
    by_tag: dict[str, list] = {}
    for i, r in enumerate(rows):
        by_tag.setdefault(r["tag"], []).append({"key": f"geneval_{i:04d}", "prompt": r["prompt"], "tag": r["tag"], "src_index": i})
    out, tags = [], list(by_tag)
    while any(by_tag.values()):  # round-robin across tags so any prefix is balanced
        for t in tags:
            if by_tag[t]:
                out.append(by_tag[t].pop(0))
    return out


def audiocaps_items(n: int) -> list[dict]:
    import pyarrow.parquet as pq
    t = pq.read_table(AUDIOCAPS).to_pylist()
    seen, out = set(), []
    for r in t:
        if r["youtube_id"] in seen:
            continue
        seen.add(r["youtube_id"])
        out.append({"key": f"audiocaps_{r['audiocap_id']}", "prompt": r["caption"], "tag": "audiocaps"})
        if len(out) >= n:
            break
    return out


# --------------------------------------------------------------------------- units

@dataclass
class Unit:
    name: str
    kind: str              # image | sfx | music | tts
    build: Callable
    items: list[dict]
    budget_min: float
    item_timeout_s: float
    pref_gpu: int
    variants: list[dict] = field(default_factory=lambda: [{}])
    text_field: str = "prompt"
    restart_between: bool = False  # fresh server per item: --gpu-only cannot offload, so memory only comes back on restart


FP16 = ["--force-fp16"]          # ComfyUI keeps the P100 in fp32 on Linux unless forced
IMG_VARIANTS = [{"server_args": FP16}, {"server_args": []}]   # fall back to fp32 on blank/failed output


def make_units() -> list[Unit]:
    P = json.loads(PROMPTS.read_text())
    gen = geneval_items()
    caps = audiocaps_items(100)
    music = [{**m, "keyscale": m["key"], "key": f"music_{i:02d}", "prompt": m["tags"],
              "tag": "instrumental" if m["lyrics"] == "[Instrumental]" else "vocal"}
             for i, m in enumerate(P["music"])]
    sents = [{"key": f"tts_{i:02d}", "prompt": s, "tag": "sentence"} for i, s in enumerate(P["tts_sentences"])]
    dialogs = [{"key": f"dialog_{i:02d}", "prompt": d, "tag": "dialog"} for i, d in enumerate(P["vibevoice_dialogs"])]
    vv_items = [{**s, "vv_text": f"[1] {s['prompt']}"} for s in sents] + [{**d, "vv_text": d["prompt"]} for d in dialogs]
    return [
        # GPU 0: images, fp16
        Unit("z-image-turbo-q8-fp16", "image", wf_zimage, gen, 80, 900, 0, variants=IMG_VARIANTS),
        Unit("flux2-klein-4b-fp16", "image", wf_klein, gen, 75, 900, 0, variants=IMG_VARIANTS),
        Unit("flux1-schnell-q8-fp16", "image", wf_flux1("flux1-schnell-Q8_0.gguf", 4, None), gen, 75, 900, 0, variants=IMG_VARIANTS),
        Unit("realvisxl-v5-fp16", "image", wf_realvis, gen, 45, 900, 0, variants=IMG_VARIANTS),
        Unit("qwen-image-2512-q4km-lightning4-fp16", "image", wf_qwen, gen, 110, 1500, 0, variants=IMG_VARIANTS),
        # GPU 1: remaining audio, then FLUX.1 dev
        Unit("stable-audio-open-1.0", "sfx", wf_sao, caps, 50, 600, 1),
        Unit("stable-audio-3-medium", "sfx", wf_sa3, caps, 40, 600, 1),
        Unit("chatterbox", "tts", wf_chatterbox, sents, 25, 300, 1),
        Unit("chatterbox-turbo", "tts", wf_chatterbox_turbo, sents, 20, 300, 1),
        # ACE-Step's audio-code LM needs CUDA; without fp16 ComfyUI puts text encoders on the CPU
        # --force-fp16 also makes the audio VAE fp16, which saturates; --gpu-only keeps fp32 with the encoder on the GPU
        # (--gpu-only never offloads, so the server is restarted between songs to avoid OOM;
        #  per-song time therefore includes loading the 10 GB checkpoint)
        Unit("ace-step-1.5-turbo", "music", wf_ace15, music, 60, 900, 1,
             variants=[{"server_args": ["--gpu-only"]}, {"server_args": FP16 + ["--fp32-vae"]}], restart_between=True),
        Unit("vibevoice-1.5b", "tts", wf_vibevoice, vv_items, 45, 600, 1,
             variants=[{"dtype": "fp16", "server_args": FP16}, {"dtype": "fp32", "server_args": FP16}], text_field="vv_text"),
        Unit("flux1-dev-q8-fp16", "image", wf_flux1("flux1-dev-Q8_0.gguf", 20, 3.5), gen, 240, 1500, 1, variants=IMG_VARIANTS),
    ]


# --------------------------------------------------------------------------- runner

class Runner:
    def __init__(self, run: Path, gen_deadline: float, only: list[str] | None,
                 max_idx: int | None = None, ignore_spent: bool = False):
        self.run = run
        self.results = run / "results.jsonl"
        self.log = Log(run / "logs" / "runner.log")
        self.deadline = gen_deadline
        self.max_idx = max_idx
        self.ignore_spent = ignore_spent
        self.units = [u for u in make_units() if not only or u.name in only]
        self.pending = list(self.units)
        self.done_keys = self.load_done()
        self.spent_min: dict[str, float] = {}
        if self.results.exists():
            for line in self.results.read_text().splitlines():
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("wall_s"):
                    self.spent_min[r["unit"]] = self.spent_min.get(r["unit"], 0.0) + r["wall_s"] / 60
        self.status: dict[str, Any] = {}

    def load_done(self) -> set[tuple[str, str]]:
        done = set()
        if self.results.exists():
            for line in self.results.read_text().splitlines():
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("status") == "success":
                    done.add((r["unit"], r["key"]))
        return done

    def record(self, row: dict) -> None:
        with LOCK:
            with self.results.open("a") as fh:
                fh.write(json.dumps(row) + "\n")

    def write_status(self) -> None:
        with LOCK:
            (self.run / "status.json").write_text(json.dumps({"updated": datetime.now().isoformat(timespec="seconds"),
                                                              "deadline": datetime.fromtimestamp(self.deadline).isoformat(timespec="minutes"),
                                                              "workers": self.status,
                                                              "pending": [u.name for u in self.pending]}, indent=2))

    def next_unit(self, gpu: int) -> Unit | None:
        with LOCK:
            for i, u in enumerate(self.pending):
                if u.pref_gpu == gpu:
                    return self.pending.pop(i)
            if self.pending:  # steal the last unit queued for the other GPU
                return self.pending.pop()
        return None

    def disk_ok(self) -> bool:
        free = shutil.disk_usage(self.run).free / 1e9
        if free < MIN_FREE_GB:
            self.log(f"DISK LOW: {free:.1f} GB free, stopping generation")
            STOP.set()
            return False
        return True

    def run_unit(self, u: Unit, srv: Server) -> None:
        t0 = now()
        spent = 0.0 if self.ignore_spent else self.spent_min.get(u.name, 0.0)
        budget_end = min(t0 + max(0.0, u.budget_min - spent) * 60, self.deadline)
        vi, ok, fails, consecutive = 0, 0, 0, 0
        stop_reason = "complete"
        if all((u.name, it["key"]) in self.done_keys for it in u.items[:self.max_idx]):
            self.log(f"gpu{srv.gpu}: SKIP {u.name}: all items already done")
            return
        srv.ensure_args(u.variants[0].get("server_args", srv.extra))
        self.log(f"gpu{srv.gpu}: START {u.name} ({len(u.items)} items, budget {u.budget_min} min, {spent:.0f} spent, "
                 f"ends {datetime.fromtimestamp(budget_end):%H:%M})")
        for idx, item in enumerate(u.items):
            if self.max_idx is not None and idx >= self.max_idx:
                stop_reason = f"reached prompt {self.max_idx}"
                break
            if (u.name, item["key"]) in self.done_keys:
                continue
            if STOP.is_set():
                stop_reason = "stopped"
                break
            if now() >= budget_end:
                stop_reason = "deadline" if budget_end >= self.deadline else "budget"
                break
            if not self.disk_ok():
                stop_reason = "disk"
                break
            seed = 1000 + idx
            if u.restart_between and (ok or fails):
                srv.restart()
            while True:
                variant = u.variants[vi]
                prefix = f"{u.name}/{item['key']}"
                text = item.get(u.text_field, item["prompt"])
                payload = item if u.kind == "music" else text
                wf = u.build(payload, seed, prefix, variant)
                timeout = max(60.0, min(u.item_timeout_s, self.deadline + 900 - now()))
                ts = now()
                try:
                    res = srv.run(wf, timeout)
                except Exception as e:
                    res = {"ok": False, "files": [], "error": f"submit: {e}"}
                wall = now() - ts
                if res["ok"] and u.kind == "image" and is_blank(res["files"][0]):
                    res = {**res, "ok": False, "error": "blank image (likely fp16 overflow)"}
                if res["ok"] and u.kind != "image":
                    bad = bad_audio(res["files"][0])
                    if bad:
                        res = {**res, "ok": False, "error": bad}
                row = {"unit": u.name, "kind": u.kind, "key": item["key"], "idx": idx, "tag": item.get("tag"),
                       "prompt": item["prompt"], "text": text if u.kind == "tts" else None, "seed": seed,
                       "variant": variant, "server_args": srv.extra, "gpu": srv.gpu, "status": "success" if res["ok"] else "error",
                       "files": res["files"], "wall_s": round(wall, 3), "error": res.get("error"),
                       "first_of_session": ok == 0 and fails == 0, "finished_at": datetime.now().isoformat(timespec="seconds")}
                self.record(row)
                if res.get("fatal") or not srv.alive():
                    srv.restart()
                if res["ok"]:
                    ok += 1
                    consecutive = 0
                    break
                fails += 1
                consecutive += 1
                self.log(f"gpu{srv.gpu}: {u.name} {item['key']} FAILED ({wall:.0f}s): {res.get('error')}")
                if ok == 0 and vi + 1 < len(u.variants):
                    vi += 1
                    self.log(f"gpu{srv.gpu}: {u.name} switching to variant {u.variants[vi]}")
                    srv.free()
                    srv.ensure_args(u.variants[vi].get("server_args", srv.extra))
                    continue
                break
            if consecutive >= 3:
                stop_reason = "3 consecutive failures"
                break
            self.status[f"gpu{srv.gpu}"] = {"unit": u.name, "ok": ok, "fails": fails, "item": idx,
                                            "last_wall_s": round(wall, 1)}
            self.write_status()
            if ok and ok % 25 == 0:
                self.log(f"gpu{srv.gpu}: {u.name} {ok} ok, last {wall:.1f}s")
        self.log(f"gpu{srv.gpu}: END {u.name}: {ok} ok, {fails} failed, {(now() - t0) / 60:.1f} min, reason={stop_reason}")
        self.record({"unit": u.name, "kind": u.kind, "key": "__unit__", "status": "unit_end", "ok": ok, "fails": fails,
                     "minutes": round((now() - t0) / 60, 2), "reason": stop_reason, "gpu": srv.gpu})
        srv.free()

    def worker(self, srv: Server) -> None:
        try:
            srv.start()
        except Exception as e:
            self.log(f"gpu{srv.gpu}: cannot start server: {e}")
            return
        while not STOP.is_set() and now() < self.deadline:
            u = self.next_unit(srv.gpu)
            if not u:
                break
            try:
                self.run_unit(u, srv)
            except Exception as e:
                self.log(f"gpu{srv.gpu}: unit {u.name} crashed: {e!r}")
                if not srv.alive():
                    try:
                        srv.restart()
                    except Exception as e2:
                        self.log(f"gpu{srv.gpu}: restart failed: {e2}")
                        return
        self.status[f"gpu{srv.gpu}"] = {"unit": None, "done": True}
        self.write_status()
        srv.stop()
        self.log(f"gpu{srv.gpu}: worker finished")


def gpu_monitor(path: Path, stop: threading.Event) -> None:
    with path.open("a") as fh:
        while not stop.is_set():
            try:
                out = subprocess.run(["nvidia-smi", "--query-gpu=timestamp,index,temperature.gpu,power.draw,utilization.gpu,memory.used,clocks.sm",
                                      "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout
                fh.write(out)
                fh.flush()
            except Exception:
                pass
            stop.wait(60)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, default=TESTS / "2026-10-07" / "comfyui-image-audio")
    ap.add_argument("--gen-deadline", default="2026-10-08T04:50", help="no new item starts after this local time")
    ap.add_argument("--score-deadline", default="2026-10-08T05:45")
    ap.add_argument("--only", nargs="*", help="run only these unit names")
    ap.add_argument("--no-score", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--gpus", type=int, nargs="*", default=[0, 1])
    ap.add_argument("--max-idx", type=int, help="stop each unit at this prompt index")
    ap.add_argument("--ignore-spent", action="store_true", help="give each unit a fresh time budget")
    a = ap.parse_args()

    if a.list:
        for u in make_units():
            print(f"{u.name:34s} {u.kind:6s} gpu{u.pref_gpu} {len(u.items):4d} items  budget {u.budget_min} min")
        return

    run = a.run_dir
    (run / "logs").mkdir(parents=True, exist_ok=True)
    deadline = datetime.fromisoformat(a.gen_deadline).timestamp()
    r = Runner(run, deadline, a.only, a.max_idx, a.ignore_spent)
    r.log(f"runner start; gen deadline {a.gen_deadline}; units: {[u.name for u in r.units]}; "
          f"{len(r.done_keys)} items already done")
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: STOP.set())
    mon_stop = threading.Event()
    threading.Thread(target=gpu_monitor, args=(run / "logs" / "gpu.csv", mon_stop), daemon=True).start()

    servers = [Server(g, run, r.log, FP16) for g in a.gpus]
    threads = [threading.Thread(target=r.worker, args=(s,)) for s in servers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for s in servers:
        s.stop()
    mon_stop.set()
    r.log("generation finished")

    if not a.no_score:
        score = HERE / "overnight_comfy_score.py"
        r.log("scoring start")
        rc = subprocess.run([str(PY), str(score), "--run-dir", str(run), "--deadline", a.score_deadline]).returncode
        r.log(f"scoring finished rc={rc}")


if __name__ == "__main__":
    main()

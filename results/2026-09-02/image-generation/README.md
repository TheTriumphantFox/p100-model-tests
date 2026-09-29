# Image generation tests — 2026-09-02

These are the existing ComfyUI image-generation test artifacts, moved into a
date/subject layout without deleting generated media.

- `pilot_geneval/` — two-prompt GenEval pilot and CLIP graphs.
- `pilot_t2i/` — two-prompt T2I-CompBench pilot.
- `realvisxl_full/` — 2,953-prompt RealVisXL run with generated images,
  manifests, CLIP scores, and graphs.
- `runtime/logs/` — ComfyUI, generation, and postprocessing logs.
- `runtime/comfyui_image_output/` — retained temporary ComfyUI output.

The manifests and logs were updated to point to these new locations. Reusable
runners and evaluators remain in `../../scripts/`, `../../tools/`, and
`../../models/` rather than being duplicated in this dated folder.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Thai Sign Language (TSL) animation generator with a Gradio web UI. It has two halves:

1. **Generation** — text → gloss lookup → SMPL-X motion → Blender render → MP4 video.
2. **Preprocessing (dataset building)** — sign video → frames → keypoints (Sapiens2) / SMPL-X params (SMPLest-X) → saved into the dataset.

The dataset is a CSV metadata table (`assets/datasets/metadata.csv`, one row per gloss/`sign_id`) plus an HDF5 file (`assets/datasets/tsl_dictionary.h5`) holding per-sign SMPL-X parameter sequences under `/{sign_id}/vertices/{param}`.

## Running

```bash
python main.py        # builds and launches the Gradio app (src/gradio_app.py:Application)
```

The app runs on the `tsl-gen` conda env (Python 3.13). Two heavyweight ML pipelines run in **separate conda envs** and are invoked as subprocesses via shell scripts — they are NOT importable from the main app:

- **Sapiens2 keypoints** — env `sapiens2`, script `scripts/inference_sapiens2.sh`, code in `sapiens2/`. Needs downloaded checkpoints under `sapiens2/sapiens2_host/` (pose + DETR detector).
- **SMPLest-X mesh/params** — env `smplestx` (the script activates `smplestx_v3`), script `scripts/inference_smplestx.sh`, code in `SMPLest-X/`. Entry point `SMPLest-X/main/inference.py`.

Setup scripts: `scripts/install.sh` (main env), `scripts/install_smplestx.sh` (SMPLest-X env). Both assume `~/anaconda3` and CUDA 12.8 wheels — paths inside the scripts are Linux/host-specific.

There is no test suite, linter config, or build step. `main.py` is the only entry point.

## Architecture

Strict layering — UI calls controllers, controllers call engine, engine touches files/subprocesses:

```
src/app/ui/*_view.py        Gradio component layout + event wiring (one tab each)
src/controllers/*.py        Orchestration + gr.Warning/Error/Info user feedback, try/except boundaries
src/engine/                 Actual work; never imports gradio for layout, only for Progress/notices
  preprocess/               video → frames → keypoints/SMPL-X → dataset persistence
  language/retrieval.py     text → gloss DataFrame (whitespace split, exact match against metadata CSV)
  generations/              dataset SMPL-X params → per-frame .pkl pose files
  visualizations/           Blender rendering, image→video
src/utils/                  config (pydantic-settings), logger, transaction
```

The four tabs are assembled in `src/gradio_app.py`: text2motion, dataset, preprocess, documents.

### Paths and config

`src/utils/config.py:AppConfig` (a frozen pydantic-settings `BaseSettings`) is the **single source of truth for every path**. It is instantiated as `self._cfg` everywhere. All paths are relative; resolve them with `self._cfg.get_path(self._cfg.SOME_PATH)` against `ROOT_DIR`. Two helpers matter:
- `get_index_file_path(path, id, index, ext, mkdir)` → `ROOT_DIR/path/{id}/{index:06d}{ext}` (the 6-digit zero-padded scheme used for frames, poses, render output — ffmpeg `%06d` patterns depend on it).
- `get_list_file_paths(path, vid, ext)` → sorted glob of those files.

When adding a new file location, add it to `AppConfig` rather than hardcoding.

### The generation pipeline (text2motion tab)

`Text2MotionController.generate_tsl_controller`:
1. `LanguageRetrieval.retrieve_glosses` — splits input on whitespace, requires **every** word to exist in the metadata CSV `gloss` column (raises `ValueError` on any miss), returns rows ordered by input.
2. `MotionGenerator.generate_sentence_motion` — reads each sign's SMPL-X param arrays from HDF5, writes one `.pkl` per frame into `tmp/motions/sentences/{motion_id}/`. `_set_frame_transition` stitches gloss frame ranges. Returns `(paths, motion_id, frame_rate, n)`.
3. `Renderer.run` — spawns `python -m src.engine.visualizations.render_script {motion_id} {target_path}` as a **subprocess** (Blender/bpy state must be isolated per render). Progress is communicated by parsing `PROGRESS:FRAME:current:total` lines from stdout.
4. `VideoPipeline.images_to_video` — ffmpeg combines `outputs/frames/{motion_id}/%06d.png` → `outputs/videos/{motion_id}.mp4`.

The dataset tab (`DatasetController.compute_mesh_controller`) follows the same render→video path but uses `generate_gloss_motion` (single sign, `tmp/motions/gloss/`).

### Rendering (Blender / bpy)

`render_script.py` is run as a subprocess, never imported. It builds a `Renderer` which drives `Blender` (`src/engine/visualizations/blender.py`):
- Installs/enables the custom addon `smplx_blender_addon_custom` (from `assets/blender/...zip`), opens `assets/blender/tsl_model.blend`, repairs missing linked files.
- Loads each per-frame `.pkl` pose via `bpy.ops.object.smplx_load_pose`.
- `configure_render_quality` auto-detects GPU backend (OPTIX→CUDA→HIP→ONEAPI→METAL, CPU fallback) and picks Cycles sample/tile/denoiser profiles accordingly.
- Renders PNGs to `outputs/frames/{motion_id}/{index:06d}`.

`bpy` (`bpy==5.1.2`) is a real dependency; `fake-bpy-module-latest` provides type stubs only.

### Dataset persistence and transactions

`DatasetIO.save_to_dataset` writes vertices to HDF5 then a row to the metadata CSV. It uses `TransactionManager` (`src/utils/transaction.py`) — register rollbacks with `add_rollback` and call `rollback()` on failure to keep CSV and HDF5 consistent. `sign_id`/`video_id` is the join key across the CSV, HDF5, and all `tmp/` subfolders; saving an existing id overwrites it.

Recent generated videos are tracked in `outputs/recents/recent.json` via `add_motion_recent` / `load_json`.

## Conventions

- Every class takes no constructor args for config/deps and instantiates `self._cfg = AppConfig()` and `self._logger = Logger()` itself. Follow this pattern.
- Logging is `src/utils/logger.py:Logger` (static methods, ANSI-colored). Pass `module="ClassName.method"` for context. There is no log file — stdout only.
- Cross-pipeline boundaries are **subprocess calls** (Sapiens2, SMPLest-X, Blender render, ffmpeg), always launched with `subprocess.Popen(..., stdout=PIPE, stderr=STDOUT, text=True, bufsize=1)` and streamed line-by-line into the logger. Reuse this pattern for new external steps.
- Controllers are the try/except + `gr.Warning`/`gr.Error`/`gr.Info` layer; the engine raises, controllers translate to UI feedback.
- Code comments and many log/UI strings are in Thai — this is intentional, keep them.
- `tmp/`, `outputs/`, `assets/`, model checkpoints, and conda envs are gitignored; the repo holds code only. Don't commit generated artifacts.
```

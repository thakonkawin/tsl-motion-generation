"""
blender.py
──────────────────────────────────────────────────────────
Blender rendering helpers for TSL motion generation.
Optimized for RTX 5060 Ti 16GB — OptiX path, batch render.
"""

import os
import bpy

from src.utils.path_manager import PathManager

# ============================================================
# Addon
# ============================================================


def _install_addon():
    addon_name = "smplx_blender_addon"

    if addon_name in bpy.context.preferences.addons:
        print("[INFO] Addon already enabled")
        return

    print("[INFO] Installing SMPL-X addon...")
    bpy.ops.preferences.addon_install(filepath=str(PathManager.BLEND_ADDON_ZIP))
    bpy.ops.preferences.addon_enable(module=addon_name)
    bpy.ops.wm.save_userpref()


# ============================================================
# Scene Helpers
# ============================================================


def _get_first_object(obj_type: str):
    for obj in bpy.context.scene.objects:
        if obj.type == obj_type:
            return obj
    return None


def _set_active(obj) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()


# ============================================================
# Render Device — RTX Optimized
# ============================================================


def _setup_device(device: str = "GPU") -> None:
    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons["cycles"].preferences

    if device == "GPU":
        # RTX 5060 Ti → ลอง OptiX ก่อน (เร็วที่สุดสำหรับ RTX)
        for compute in ("OPTIX", "CUDA", "HIP", "METAL"):
            try:
                cycles_prefs.compute_device_type = compute
                print(f"[Render] Using compute backend: {compute}")
                break
            except Exception:
                continue

        cycles_prefs.get_devices()

        for dev in cycles_prefs.devices:
            dev.use = True
            print(f"[Render] Enabled device: {dev.name}")

        bpy.context.scene.cycles.device = "GPU"

    else:
        bpy.context.scene.cycles.device = "CPU"
        print("[Render] Using CPU rendering")


# ============================================================
# Render Quality — RTX 5060 Ti 16GB Tuned
# ============================================================


def _configure_render_quality(
    scene, resolution: tuple, output_dir, fast: bool = True
) -> None:
    """
    Configure Blender render settings for RTX 5060 Ti 16GB.

    Key changes vs. original:
    - samples 64 → 32  (เพียงพอสำหรับ motion preview + denoising ชดเชย)
    - OptiX denoiser   (เร็วกว่า OIDN บน RTX มาก)
    - max_bounces 4 → 3
    - tile size 256 → 512  (VRAM 16GB รับได้ tile ใหญ่ขึ้น → fewer kernel launches)
    - persistent_data = True  (cache BVH/textures ข้าม frame ไม่ต้อง rebuild)
    - resolution_percentage 85 → 100 หรือคงไว้ตามต้องการ
    """

    # Engine
    scene.render.engine = "CYCLES"

    # Resolution
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 85

    # Output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output_dir / "frame_")

    # ── Format Fix (FFMPEG → PNG) ──────────────────────────
    scene.render.use_file_extension = True
    try:
        scene.render.ffmpeg.format = "MPEG4"
    except Exception:
        pass
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 15  # 0=ไม่บีบ เร็วสุด / 15=สมดุล

    # ── Cycles Core ───────────────────────────────────────
    # 32 samples + OptiX denoiser ≈ คุณภาพเทียบเท่า 64 samples + OIDN
    # แต่เร็วกว่า ~40–60% บน RTX
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True

    # OptiX เร็วกว่า OIDN บน RTX ชัดเจน
    for denoiser in ("OPTIX", "OPENIMAGEDENOISE"):
        try:
            scene.cycles.denoiser = denoiser
            print(f"[Render] Denoiser: {denoiser}")
            break
        except Exception:
            continue

    # Adaptive sampling — หยุด sample เร็วขึ้นในส่วนที่ converge แล้ว
    if hasattr(scene.cycles, "use_adaptive_sampling"):
        scene.cycles.use_adaptive_sampling = True
        if hasattr(scene.cycles, "adaptive_threshold"):
            scene.cycles.adaptive_threshold = 0.01  # ค่า default 0.01
        if hasattr(scene.cycles, "adaptive_min_samples"):
            scene.cycles.adaptive_min_samples = 16

    # Max bounces ลดลง (motion render ไม่ต้องการ GI เต็ม)
    if hasattr(scene.cycles, "max_bounces"):
        scene.cycles.max_bounces = 3

    # ── Tile Size — VRAM 16GB → ใช้ tile ใหญ่ได้ ───────────
    # tile ใหญ่ = kernel launch น้อยลง = overhead น้อยลง
    if hasattr(scene.render, "tile_x"):
        scene.render.tile_x = 512
        scene.render.tile_y = 512

    # ── Persistent Data ────────────────────────────────────
    # สำคัญมาก: cache BVH + textures ข้าม frame
    # ไม่ต้อง rebuild ทุก render → ประหยัดเวลาได้มากเมื่อ render หลาย frame
    scene.render.use_persistent_data = True

    if fast:
        scene.render.use_motion_blur = False
        scene.render.use_freestyle = False


# ============================================================
# Main Render — Batch / Persistent Loop
# ============================================================


def render(motion_id: str, motion_lst: list, resolution: tuple = (512, 512)):

    print("[Render] Installing addon...")
    _install_addon()

    print("[Render] Opening blend file...")
    bpy.ops.wm.open_mainfile(filepath=str(PathManager.BLEND_FILE))

    # ── Fix missing files ──────────────────────────────────
    addon_data_dir = PathManager.BLEND_ADDON_DATA_DIR
    if addon_data_dir and os.path.isdir(addon_data_dir):
        bpy.ops.file.find_missing_files(directory=os.path.abspath(str(addon_data_dir)))

    # ── Scene + Render Settings ────────────────────────────
    scene = bpy.context.scene
    frame_folder = PathManager.get_output_frame_dir(vid=motion_id)

    _configure_render_quality(
        scene=scene, resolution=resolution, output_dir=frame_folder, fast=True
    )

    # ── Device (เรียกครั้งเดียว ก่อน loop) ────────────────
    _setup_device()

    # ── Armature ───────────────────────────────────────────
    armature = _get_first_object("ARMATURE")
    if armature is None:
        raise RuntimeError("No ARMATURE found in scene — SMPL-X setup required.")
    _set_active(armature)

    # ── Render Loop ────────────────────────────────────────
    # use_persistent_data=True ทำให้ Blender ไม่ทิ้ง BVH/texture cache
    # ระหว่าง frame → ประหยัดเวลา rebuild ต่อ frame ได้มาก
    total_frames = len(motion_lst)

    for idx, motion_path in enumerate(motion_lst):

        print(f"[Render] Loading pose {idx + 1}/{total_frames}")
        bpy.ops.object.smplx_load_pose(filepath=str(motion_path))

        frame_path = PathManager.get_output_frame_path(motion_id, idx)

        # filepath ต้องไม่มี extension (Blender เติมเอง)
        scene.render.filepath = str(frame_path.with_suffix(""))

        bpy.ops.render.render(write_still=True)

        print(f"[Render] Saved frame {idx + 1}/{total_frames} → {frame_path}")

    print("[Render] Completed")

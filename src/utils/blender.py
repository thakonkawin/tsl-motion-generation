"""
blender.py
──────────────────────────────────────────────────────────
Blender rendering helpers for TSL motion generation.
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
# Render Device
# ============================================================


def _setup_device(device: str = "GPU") -> None:
    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons["cycles"].preferences

    if device == "GPU":

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
# Render Quality
# ============================================================


def _configure_render_quality(
    scene, resolution: tuple, output_dir, fast: bool = True
) -> None:
    """
    Configure Blender render settings safely.
    """

    # --------------------------------------------------
    # Engine
    # --------------------------------------------------
    scene.render.engine = "CYCLES"

    # --------------------------------------------------
    # Resolution
    # --------------------------------------------------
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 85

    # --------------------------------------------------
    # Output directory
    # --------------------------------------------------
    output_dir.mkdir(parents=True, exist_ok=True)

    # Blender expects prefix path here
    scene.render.filepath = str(output_dir / "frame_")

    # --------------------------------------------------
    # IMPORTANT FIX
    # --------------------------------------------------
    # Reset movie settings BEFORE switching to PNG
    #
    # Some .blend files save output mode as FFMPEG,
    # which causes:
    #
    # TypeError:
    # enum "PNG" not found in ('FFMPEG')
    #
    # --------------------------------------------------

    scene.render.use_file_extension = True

    try:
        # reset format container first
        scene.render.ffmpeg.format = "MPEG4"
    except Exception:
        pass

    # now switch to image sequence
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 15

    # --------------------------------------------------
    # Cycles
    # --------------------------------------------------
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True

    try:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass

    # --------------------------------------------------
    # Tile Size (Blender 3.x)
    # --------------------------------------------------
    if hasattr(scene.render, "tile_x"):
        scene.render.tile_x = 256
        scene.render.tile_y = 256

    # --------------------------------------------------
    # Fast Preview
    # --------------------------------------------------
    if fast:

        scene.render.use_motion_blur = False
        scene.render.use_freestyle = False

        if hasattr(scene.cycles, "use_adaptive_sampling"):
            scene.cycles.use_adaptive_sampling = True

        if hasattr(scene.cycles, "max_bounces"):
            scene.cycles.max_bounces = 4


# ============================================================
# Main Render
# ============================================================


def render(motion_id: str, motion_lst: list, resolution: tuple = (512, 512)):

    print("[Render] Installing addon...")
    _install_addon()

    print("[Render] Opening blend file...")
    bpy.ops.wm.open_mainfile(filepath=str(PathManager.BLEND_FILE))

    # --------------------------------------------------
    # Fix missing files
    # --------------------------------------------------
    addon_data_dir = PathManager.BLEND_ADDON_DATA_DIR

    if addon_data_dir and os.path.isdir(addon_data_dir):

        bpy.ops.file.find_missing_files(directory=os.path.abspath(str(addon_data_dir)))

    # --------------------------------------------------
    # Scene
    # --------------------------------------------------
    scene = bpy.context.scene

    # --------------------------------------------------
    # Render settings
    # --------------------------------------------------
    frame_folder = PathManager.get_output_frame_dir(vid=motion_id)

    _configure_render_quality(
        scene=scene, resolution=resolution, output_dir=frame_folder, fast=True
    )

    # --------------------------------------------------
    # Device
    # --------------------------------------------------
    _setup_device()

    # --------------------------------------------------
    # Armature
    # --------------------------------------------------
    armature = _get_first_object("ARMATURE")

    if armature is None:
        raise RuntimeError("No ARMATURE found in scene — SMPL-X setup required.")

    _set_active(armature)

    # --------------------------------------------------
    # Render Loop
    # --------------------------------------------------
    total_frames = len(motion_lst)

    for idx, motion_path in enumerate(motion_lst):

        print(f"[Render] Loading pose {idx + 1}/{total_frames}")

        bpy.ops.object.smplx_load_pose(filepath=str(motion_path))

        frame_path = PathManager.get_output_frame_path(motion_id, idx)

        # IMPORTANT:
        # filepath must NOT include extension
        scene.render.filepath = str(frame_path.with_suffix(""))

        bpy.ops.render.render(write_still=True)

        print(f"[Render] Saved frame " f"{idx + 1}/{total_frames} → {frame_path}")

    print("[Render] Completed")

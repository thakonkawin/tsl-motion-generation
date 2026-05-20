import os
from typing import Any

import bpy

from src.utils.config import AppConfig
from src.utils.logger import Logger


class Blender:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def install_addon(self) -> None:
        addon_name = self._cfg.BLEND_ADDON_NAME

        if addon_name in bpy.context.preferences.addons:
            self._logger.info(message="Addon already enabled")
            return

        zip_file = self._cfg.get_path(path=self._cfg.BLEND_ADDON_ZIP)
        if not zip_file.exists():
            msg = f"Addon zip not found: {zip_file}"
            self._logger.error(message=msg, module="Blender._install_addon")
            raise FileNotFoundError(msg)

        bpy.ops.preferences.addon_install(filepath=str(zip_file))
        bpy.ops.preferences.addon_enable(module=addon_name)
        bpy.ops.wm.save_userpref()

    def get_first_object(self, obj_type: str) -> Any:
        for obj in bpy.context.scene.objects:
            if obj.type == obj_type:
                return obj
        return None

    def set_active(self, obj: Any) -> None:
        if obj is None:
            msg = "Object is None"
            self._logger.error(message=msg, module="Blender._install_addon")
            raise ValueError(msg)

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()

    def set_addon(self) -> None:

        self._logger.info(message="[Render] Opening blend file...")
        bpy.ops.wm.open_mainfile(
            filepath=str(self._cfg.get_path(path=self._cfg.BLEND_FILE))
        )

        # ── Fix missing files ──────────────────────────────────
        addon_data_dir = self._cfg.get_path(path=self._cfg.BLEND_ADDON_DATA_DIR)
        if addon_data_dir and os.path.isdir(addon_data_dir):
            bpy.ops.file.find_missing_files(
                directory=os.path.abspath(str(addon_data_dir))
            )

    def configure_render_quality(self, scene, resolution: tuple) -> None:
        # Engine
        scene.render.engine = "CYCLES"
        # GPU Auto-Detection
        prefs = bpy.context.preferences
        cycles_prefs = prefs.addons["cycles"].preferences
        BACKEND_PRIORITY = ["OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"]
        # Per-backend optimal settings
        # (tile_size, samples, min_samples, denoiser)
        BACKEND_PROFILES = {
            "OPTIX": (512, 64, 32, "OPTIX"),
            "CUDA": (256, 96, 48, "OPENIMAGEDENOISE"),
            "HIP": (256, 96, 48, "OPENIMAGEDENOISE"),
            "ONEAPI": (128, 128, 64, "OPENIMAGEDENOISE"),
            "METAL": (256, 128, 64, "OPENIMAGEDENOISE"),
            None: (64, 256, 128, "OPENIMAGEDENOISE"),  # CPU fallback
        }
        selected_backend = None
        detected_gpu_names = []
        for backend in BACKEND_PRIORITY:
            try:
                cycles_prefs.compute_device_type = backend
                cycles_prefs.refresh_devices()
                gpu_devices = [d for d in cycles_prefs.devices if d.type != "CPU"]
                if not gpu_devices:
                    continue
                for device in cycles_prefs.devices:
                    device.use = device.type != "CPU"
                selected_backend = backend
                detected_gpu_names = [d.name for d in gpu_devices if d.use]
                break
            except Exception:
                continue
        # CPU fallback
        if selected_backend:
            scene.cycles.device = "GPU"
        else:
            cycles_prefs.compute_device_type = "NONE"
            scene.cycles.device = "CPU"
        # Unpack profile for selected backend
        tile_size, samples, min_samples, denoiser = BACKEND_PROFILES[selected_backend]
        # Resolution
        scene.render.resolution_x = resolution[0]
        scene.render.resolution_y = resolution[1]
        scene.render.resolution_percentage = 100
        # Output Format
        scene.render.use_file_extension = True
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGB"
        scene.render.image_settings.color_depth = "8"
        scene.render.image_settings.compression = 0
        # Color Management
        scene.display_settings.display_device = "sRGB"
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0
        scene.sequencer_colorspace_settings.name = "sRGB"
        # Metadata
        scene.render.use_stamp = False
        # Sampling
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.samples = samples
        scene.cycles.adaptive_min_samples = min_samples
        scene.cycles.adaptive_threshold = 0.01
        # Denoising
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = denoiser
        scene.cycles.denoising_prefilter = "FAST"
        scene.cycles.use_preview_denoising = False
        # Light & Noise
        scene.cycles.use_light_tree = True
        scene.cycles.sample_clamp_indirect = 3.0
        scene.cycles.blur_glossy = 0.5
        # Bounces
        scene.cycles.max_bounces = 6
        scene.cycles.diffuse_bounces = 2
        scene.cycles.glossy_bounces = 2
        scene.cycles.transmission_bounces = 4
        scene.cycles.volume_bounces = 0
        scene.cycles.transparent_max_bounces = 4
        # Performance
        scene.cycles.use_auto_tile = True
        scene.cycles.tile_size = tile_size
        scene.render.threads_mode = "AUTO"
        scene.render.use_persistent_data = True
        # Disable Unused Features
        scene.render.use_motion_blur = False
        scene.render.use_freestyle = False
        # Summary Log
        gpu_label = ", ".join(detected_gpu_names) if detected_gpu_names else "CPU"
        mgs = str(
            f"[Render] Device={scene.cycles.device} | "
            f"Backend={selected_backend or 'CPU'} | "
            f"GPU={gpu_label} | "
            f"Samples={samples} (min={min_samples}) | "
            f"Tile={tile_size} | "
            f"Denoiser={denoiser}"
        )
        self._logger.info(message=mgs)

    def get_scene(self) -> Any:
        return bpy.context.scene

    def smplx_load_pose(self, motion_path: str) -> None:
        bpy.ops.object.smplx_load_pose(filepath=motion_path)  # pyright: ignore[reportAttributeAccessIssue]

    def render(self) -> None:
        bpy.ops.render.render(write_still=True)

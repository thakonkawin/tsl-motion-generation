import subprocess
import sys
from pathlib import Path

from src.engine.visualizations.blender import Blender
from src.utils.config import AppConfig
from src.utils.logger import Logger


class Renderer:
    def __init__(
        self, motion_id: str, motion_list: list, resolution: tuple = (512, 512)
    ) -> None:
        self._cfg = AppConfig()
        self._logger = Logger()
        self._blender = Blender()
        self.motion_id = motion_id
        self.motion_list = motion_list
        self.resolution = resolution

    def render(self):

        self._blender.install_addon()
        self._blender.set_addon()

        scene = self._blender.get_scene()
        self._blender.configure_render_quality(scene=scene, resolution=self.resolution)

        # Armature
        armature = self._blender.get_first_object(obj_type="ARMATURE")
        if armature is None:
            msg = "No ARMATURE found in scene — SMPL-X setup required."
            self._logger.error(message=msg, module="Renderer.render")
            raise RuntimeError(msg)

        self._blender.set_active(obj=armature)

        # Render Loop
        total_frames = len(self.motion_list)

        for idx, motion_path in enumerate(self.motion_list):
            self._logger.info(message=f"[Render] Loading pose {idx + 1}/{total_frames}")

            self._blender.smplx_load_pose(motion_path=str(motion_path))

            frame_path = self._cfg.get_index_file_path(
                path=self._cfg.OUTPUT_FRAME_DIR, id=self.motion_id, index=idx
            )

            scene.render.filepath = str(frame_path.with_suffix(""))

            self._blender.render()
            self._logger.info(
                message=f"[Render] Saved frame {idx + 1}/{total_frames} → {frame_path}"
            )

        self._logger.success("[Render] Completed")

    def run(self, sign_id: str, target_path: Path) -> None:
        try:
            cmd = [
                sys.executable,
                "-m",
                "src.engine.visualizations.render_script",
                sign_id,
                str(target_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                self._logger.error(message=result.stderr, module="Renderer.run")
                raise RuntimeError(f"Subprocess failed:\n{result.stderr}")

            return None

        except Exception as e:
            msg = f"Render invalid.{e}"
            self._logger.error(message=msg, module="Renderer.run")
            raise RuntimeError(msg)

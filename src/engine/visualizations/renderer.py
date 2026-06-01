import subprocess
import sys
from pathlib import Path

import gradio as gr

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
        smplx_obj = self._blender.get_object("SMPLX-mesh-neutral")
        self._blender.set_active(smplx_obj)

        # Render Loop
        total_frames = len(self.motion_list)

        for idx, motion_path in enumerate(self.motion_list):
            self._logger.info(message=f"[Render] Loading pose {idx + 1}/{total_frames}")

            self._blender.smplx_load_pose(motion_path=str(motion_path))
            print(f"PROGRESS:FRAME:{idx + 1}:{total_frames}", flush=True)

            frame_path = self._cfg.get_index_file_path(
                path=self._cfg.OUTPUT_FRAME_DIR, id=self.motion_id, index=idx
            )

            scene.render.filepath = str(frame_path.with_suffix(""))

            self._blender.render()
            self._logger.info(
                message=f"[Render] Saved frame {idx + 1}/{total_frames} → {frame_path}"
            )

        self._logger.success("[Render] Completed")

    def run(
        self,
        sign_id: str,
        target_path: Path,
        progress: gr.Progress,
    ) -> None:

        try:
            cmd = [
                sys.executable,
                "-m",
                "src.engine.visualizations.render_script",
                sign_id,
                str(target_path),
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            if process.stdout is None:
                raise RuntimeError("stdout pipe not available")

            for line in process.stdout:
                line = line.strip()

                if line.startswith("PROGRESS:FRAME:"):
                    parts = line.split(":")

                    current = int(parts[2])
                    total = int(parts[3])

                    progress(
                        current / total, desc=f"Rendering... {current}/{total} frames"
                    )

            process.wait()

            if process.returncode != 0:
                stderr = ""

                if process.stderr is not None:
                    stderr = process.stderr.read()

                self._logger.error(
                    message=stderr,
                    module="Renderer.run",
                )

                raise RuntimeError(f"Subprocess failed:\n{stderr}")

        except Exception as e:
            msg = f"Render invalid. {e}"

            self._logger.error(
                message=msg,
                module="Renderer.run",
            )

            raise RuntimeError(msg)

import shutil

# import imageio
import subprocess
import uuid
from pathlib import Path

import cv2

from src.utils.config import AppConfig
from src.utils.logger import Logger


class VideoPipeline:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def upload_sign_video(
        self, upload_file: str
    ) -> tuple[str, float, list[tuple[str, str]], int]:

        sign_id = str(uuid.uuid4())
        frame_paths: list[str] = []

        video_path = self._cfg.get_path(
            self._cfg.TMP_UPLOAD_VIDEO_DIR / f"{sign_id}.mp4"
        )

        video_path.parent.mkdir(parents=True, exist_ok=True)

        if video_path is None:
            msg = f"could not resolve video path {video_path}"
            self._logger.error(message=msg, module="VideoPipeline.upload_sign_video")
            raise ValueError(msg)

        shutil.copy(upload_file, str(video_path))

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        idx = 1
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame_path = self._cfg.get_index_file_path(
                path=self._cfg.TMP_UPLOAD_FRAME_DIR,
                id=sign_id,
                index=idx,
                ext=".jpg",
                mkdir=True,
            )

            if frame_path is None:
                msg = f"could not resolve frame path: {idx}"
                self._logger.error(
                    message=msg, module="VideoPipeline.upload_sign_video"
                )
                raise ValueError(msg)

            ok = cv2.imwrite(str(frame_path), frame)
            if not ok:
                msg = f"could not save frame: {frame_path}"
                self._logger.error(
                    message=msg, module="VideoPipeline.upload_sign_video"
                )
                raise ValueError(msg)

            frame_paths.append(str(frame_path))
            idx += 1

        cap.release()

        gallery_items = [(path, str(i)) for i, path in enumerate(frame_paths, start=1)]

        return sign_id, fps, gallery_items, len(frame_paths)

    def images_to_video(
        self,
        motion_id: str,
        frame_rate: int = 30,
    ) -> Path | None:

        image_dir = self._cfg.get_path(path=self._cfg.OUTPUT_FRAME_DIR / motion_id)

        image_paths = sorted(image_dir.glob("*.png"))

        if not image_paths:
            self._logger.error(
                message="No PNG images found",
                module="VideoPipeline.images_to_video",
            )

            return None

        output_path = self._cfg.get_path(
            path=self._cfg.OUTPUT_VIDEO_DIR / f"{motion_id}.mp4"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        input_pattern = str(image_dir / "%06d.png")

        cmd = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(frame_rate),
            "-start_number",
            "0",
            "-i",
            input_pattern,
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]

        self._logger.info(
            message=f"Running ffmpeg command: {' '.join(cmd)}",
            module="VideoPipeline.images_to_video",
        )

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            output_lines = []

            if process.stdout is None:
                raise RuntimeError("Failed to capture subprocess stdout")

            for line in process.stdout:
                line = line.rstrip()

                if line:
                    output_lines.append(line)

                    self._logger.info(
                        message=line,
                        module="VideoPipeline.images_to_video",
                    )

            return_code = process.wait()

            if return_code != 0:
                msg = f"FFmpeg failed with return code {return_code}\n" + "\n".join(
                    output_lines
                )

                self._logger.error(
                    message=msg,
                    module="VideoPipeline.images_to_video",
                )

                return None

            self._logger.info(
                message=f"Video generated successfully: {output_path}",
                module="VideoPipeline.images_to_video",
            )

            return output_path

        except Exception as e:
            self._logger.error(
                message=str(e),
                module="VideoPipeline.smplx_estimator",
            )

            return None

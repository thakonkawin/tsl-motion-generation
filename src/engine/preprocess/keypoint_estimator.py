import subprocess

# from os import error
from src.utils.config import AppConfig
from src.utils.logger import Logger


class KeypointEstimator:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def kepoint_estimator(self, video_id: str) -> list[tuple[str, str]]:

        script_path = self._cfg.get_path(self._cfg.INFERENCE_SAPIENS2_SCRIPT)

        input_path = self._cfg.get_path(self._cfg.TMP_UPLOAD_FRAME_DIR / video_id)

        if not input_path.exists():
            msg = f"Input video not found: {input_path}"

            self._logger.error(
                message=msg,
                module="KeypointEstimator.kepoint_estimator",
            )

            raise FileNotFoundError(msg)

        output_path = self._cfg.get_path(self._cfg.TMP_KEYPOINT_DIR / video_id)
        output_path.mkdir(parents=True, exist_ok=True)

        if not output_path.exists():
            msg = f"Output video not found: {output_path}"

            self._logger.error(
                message=msg,
                module="KeypointEstimator.kepoint_estimator",
            )

            raise FileNotFoundError(msg)

        cmd = [
            "bash",
            str(script_path),
            str(input_path),
            str(output_path),
        ]

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
                        module="KeypointEstimator.kepoint_estimator",
                    )
            return_code = process.wait(timeout=300)

            if return_code != 0:
                raise subprocess.CalledProcessError(
                    returncode=return_code,
                    cmd=cmd,
                    output="\n".join(output_lines),
                )

            image_exts = {".jpg", ".jpeg", ".png"}
            image_paths = sorted(
                p for p in output_path.iterdir() if p.suffix.lower() in image_exts
            )
            gallery_items = [
                (str(path), str(i)) for i, path in enumerate(image_paths, start=1)
            ]

            return gallery_items

        except subprocess.CalledProcessError as e:
            msg = f"Sapiens2 inference failed:\n{e.output}"

            self._logger.error(
                message=msg,
                module="KeypointEstimator.kepoint_estimator",
            )

            raise RuntimeError(msg) from e

        except subprocess.TimeoutExpired as e:
            msg = "Sapiens2 inference timeout"

            self._logger.error(
                message=msg,
                module="KeypointEstimator.kepoint_estimator",
            )

            raise TimeoutError(msg) from e

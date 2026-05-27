import subprocess
from pathlib import Path

from src.utils.config import AppConfig
from src.utils.logger import Logger


class SMPLXEstimator:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def smplx_estimator(self, video_id: str, frame_rate: int) -> Path:

        script_path = self._cfg.get_path(self._cfg.INFERENCE_SMPLESTX_SCRIPT)

        input_path = self._cfg.get_path(
            self._cfg.TMP_UPLOAD_VIDEO_DIR / f"{video_id}.mp4"
        )

        if not input_path.exists():
            msg = f"Input video not found: {input_path}"

            self._logger.error(
                message=msg,
                module="SMPLXEstimator.smplx_estimator",
            )

            raise FileNotFoundError(msg)

        cmd = [
            "bash",
            str(script_path),
            "smplest_x_h",
            str(input_path),
            str(frame_rate),
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
                        module="SMPLXEstimator.smplx_estimator",
                    )
            return_code = process.wait(timeout=300)

            if return_code != 0:
                raise subprocess.CalledProcessError(
                    returncode=return_code,
                    cmd=cmd,
                    output="\n".join(output_lines),
                )

            result_path = self._cfg.get_path(
                self._cfg.TMP_MESH_DIR / f"result_{video_id}.mp4"
            )

            if not result_path.exists():
                msg = f"Result video not found: {result_path}"

                self._logger.error(
                    message=msg,
                    module="SMPLXEstimator.smplx_estimator",
                )

                raise FileNotFoundError(msg)

            return result_path

        except subprocess.CalledProcessError as e:
            msg = f"SMPLest-X inference failed:\n{e.output}"

            self._logger.error(
                message=msg,
                module="SMPLXEstimator.smplx_estimator",
            )

            raise RuntimeError(msg) from e

        except subprocess.TimeoutExpired as e:
            msg = "SMPLest-X inference timeout"

            self._logger.error(
                message=msg,
                module="SMPLXEstimator.smplx_estimator",
            )

            raise TimeoutError(msg) from e

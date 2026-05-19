import subprocess
from pathlib import Path

from src.utils.config import AppConfig
from src.utils.logger import Logger


class SMPLXEstimator:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def smplestx_estimator(self, video_id: str, frame_rate: int) -> Path | None:

        script_path = self._cfg.get_path(self._cfg.INFERENCE_SMPLESTX_SCRIPT)

        input_path = self._cfg.get_path(
            self._cfg.TMP_UPLOAD_VIDEO_DIR / f"{video_id}.mp4"
        )

        cmd = ["bash", script_path, "smplest_x_h", input_path, str(frame_rate)]

        try:
            subprocess.run(cmd, check=True)

            result_path = self._cfg.get_path(
                self._cfg.TMP_MESH_DIR / f"result_{video_id}.mp4"
            )
            if not result_path.exists():
                msg = f"could not resolve video path {result_path}"
                self._logger.error(
                    message=msg, module="SMPLXEstimator.smplestx_estimator"
                )
                raise FileExistsError(msg)

            return result_path

        except Exception as e:
            msg = f"Invalid of SMPLest-X {e}"
            self._logger.error(message=msg, module="SMPLXEstimator.smplestx_estimator")
            raise ValueError(msg)

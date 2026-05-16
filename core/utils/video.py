import shutil
from pathlib import Path
from typing import Any

from core.utils.exceptions import (
    FileOperationError,
)


class VideoUtils:
    @staticmethod
    def load_video(video_path: str) -> Any:
        raise NotImplementedError

    @staticmethod
    def export_video(frames: list[Any], output_path: str) -> str:
        raise NotImplementedError

    @staticmethod
    def copy_video_file(
        source: str,
        destination: Path,
    ) -> None:

        try:
            shutil.copy(
                source,
                str(destination),
            )

        except Exception as err:
            raise FileOperationError(f"failed to copy file: {err}") from err

import shutil
from pathlib import Path

from core.utils.exceptions import (
    FileOperationError,
)


class FileUtil:
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

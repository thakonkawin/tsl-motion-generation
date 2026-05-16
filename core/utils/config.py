from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent

    TEMP_DIR: str = "tmp"

    UPLOADS_DIR: str = "uploads"

    VIDEOS_DIR: str = "videos"

    FRAMES_DIR: str = "frames"

    FRAME_EXT: str = ".jpg"

    DEFAULT_VIDEO_EXT: str = ".mp4"

    ALLOWED_VIDEO_EXTENSIONS: tuple[str, ...] = (
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
    )

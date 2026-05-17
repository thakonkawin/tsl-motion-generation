from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Dataset
    METADATA_PATH: str = "assets/datasets/metadata.csv"
    DATASET_PATH: str = "assets/datasets/tsl_dictionary.h5"

    MOTION_SENTENCE_DIR: str = "tmp/motions/sentences"

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

    MOTION_MODEL_PATH: str = ""
    HUMAN_MODEL_PATH: str = ""
    KEYPOINT_MODEL_PATH: str = ""

    CSS_PATH = ROOT_DIR / "core/ui/components/styles.css"

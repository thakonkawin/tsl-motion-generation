from enum import IntEnum, StrEnum


class PathConfig(StrEnum):
    # Upload
    UPLOAD_DIR = "upload"
    UPLOAD_VIDEO_DIR = "upload/videos"
    UPLOAD_FRAME_DIR = "upload/frames"


DATASET_HEADERS: list[str] = [
    "sign_id",
    "gloss",
    "fps",
    "num_frames",
    "frame_start",
    "frame_end",
]


class Resolution(IntEnum):
    SD = 480
    HD = 720
    FHD = 1080


# ค่าที่ไม่เป็น group ใช้ constant ธรรมดา
DEFAULT_FPS = 30
DEFAULT_RESOLUTION = Resolution.HD

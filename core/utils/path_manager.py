from pathlib import Path

from core.utils.config import AppConfig


class PathManager:
    @classmethod
    def root_dir(cls) -> Path:
        return AppConfig.ROOT_DIR

    # ====================== Dataset ======================
    @classmethod
    def metadata_path(cls) -> Path:
        return AppConfig.ROOT_DIR / AppConfig.METADATA_PATH

    @classmethod
    def temp_dir(cls) -> Path:
        return cls.root_dir() / AppConfig.TEMP_DIR

    # ====================== Upload ======================
    @classmethod
    def uploads_dir(cls) -> Path:
        return cls.temp_dir() / AppConfig.UPLOADS_DIR

    @classmethod
    def upload_videos_dir(cls) -> Path:
        return cls.uploads_dir() / AppConfig.VIDEOS_DIR

    @classmethod
    def upload_frames_dir(cls) -> Path:
        return cls.uploads_dir() / AppConfig.FRAMES_DIR

    @classmethod
    def upload_video_path(
        cls,
        video_id: str,
        ext: str,
    ) -> Path:

        return cls.upload_videos_dir() / f"{video_id}{ext}"

    @classmethod
    def upload_frame_process_dir(
        cls,
        video_id: str,
    ) -> Path:

        return cls.upload_frames_dir() / video_id

    @classmethod
    def upload_frame_path(
        cls,
        video_id: str,
        frame_index: int,
    ) -> Path:

        return (
            cls.upload_frame_process_dir(video_id)
            / f"{frame_index:06d}{AppConfig.FRAME_EXT}"
        )

    # ====================== Temp ======================

    @classmethod
    def ensure_dirs(cls):

        directories = [
            cls.temp_dir(),
            # Upload
            cls.uploads_dir(),
            cls.upload_videos_dir(),
            cls.upload_frames_dir(),
            # Temp
        ]

        for directory in directories:
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

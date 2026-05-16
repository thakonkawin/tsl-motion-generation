from pathlib import Path

from src.utils.config import PathConfig


class PathManager:
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent

    @classmethod
    def ensure_dirs(cls):

        dirs = [
            cls.ROOT_DIR / PathConfig.UPLOAD_DIR,
            cls.ROOT_DIR / PathConfig.UPLOAD_VIDEO_DIR,
            cls.ROOT_DIR / PathConfig.UPLOAD_FRAME_DIR,
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def create_process_directory(
        cls,
        target_dir: str,
        dir_id: str,
    ) -> Path:

        path = cls.ROOT_DIR / target_dir / dir_id

        path.mkdir(parents=True, exist_ok=True)

        return path

    @classmethod
    def get_process_directory(
        cls,
        target_dir: str,
        dir_id: str,
    ) -> Path:

        return cls.ROOT_DIR / target_dir / dir_id

    @classmethod
    def get_file_path(
        cls,
        target_dir: str,
        file_id: str,
        ext: str,
    ) -> Path:

        return cls.ROOT_DIR / target_dir / f"{file_id}.{ext}"

    @classmethod
    def get_process_file_path(
        cls,
        target_dir: str,
        dir_id: str,
        index: int,
        ext: str = "jpg",
    ) -> Path:

        process_dir = cls.create_process_directory(
            target_dir=target_dir,
            dir_id=dir_id,
        )

        return process_dir / f"{index:04d}.{ext}"

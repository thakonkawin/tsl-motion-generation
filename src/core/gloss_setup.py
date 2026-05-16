import shutil
import uuid

import cv2

from src.utils.config import PathConfig
from src.utils.object_manager import PathManager


class GlossSetup:
    @staticmethod
    def upload_sign_video(
        upload_file: str,
        video_ext: str,
    ) -> tuple[str, float, list[tuple[str, str]], int]:

        vid = str(uuid.uuid4())
        frame_paths: list[str] = []

        # video path
        video_path = PathManager.get_file_path(
            target_dir=PathConfig.UPLOAD_VIDEO_DIR,
            file_id=vid,
            ext=video_ext,
        )

        if video_path is None:
            raise ValueError("could not resolve video path")

        # frame folder
        frame_folder = PathManager.get_process_directory(
            target_dir=PathConfig.UPLOAD_FRAME_DIR,
            dir_id=vid,
        )

        if frame_folder is None:
            raise ValueError("could not resolve frame folder")

        frame_folder.mkdir(parents=True, exist_ok=True)
        shutil.copy(upload_file, str(video_path))

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        idx = 1
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame_path = PathManager.get_process_file_path(
                target_dir=PathConfig.UPLOAD_FRAME_DIR,
                dir_id=vid,
                index=idx,
            )

            if frame_path is None:
                raise ValueError(f"could not resolve frame path: {idx}")

            success = cv2.imwrite(str(frame_path), frame)
            if not success:
                raise ValueError(f"could not save frame: {frame_path}")

            frame_paths.append(str(frame_path))
            idx += 1

        cap.release()

        gallery_items = [(path, str(i)) for i, path in enumerate(frame_paths, start=1)]

        return vid, fps, gallery_items, len(frame_paths)

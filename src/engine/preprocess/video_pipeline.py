import shutil
import uuid

import cv2

from src.utils.config import AppConfig
from src.utils.logger import Logger


class VideoPipeline:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def upload_sign_video(
        self, upload_file: str
    ) -> tuple[str, float, list[tuple[str, str]], int]:

        sign_id = str(uuid.uuid4())
        frame_paths: list[str] = []

        video_path = self._cfg.get_path(
            self._cfg.TMP_UPLOAD_VIDEO_DIR / f"{sign_id}.mp4"
        )

        video_path.parent.mkdir(parents=True, exist_ok=True)

        if video_path is None:
            msg = f"could not resolve video path {video_path}"
            self._logger.error(message=msg, module="VideoPipeline.upload_sign_video")
            raise ValueError(msg)

        shutil.copy(upload_file, str(video_path))

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        idx = 1
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame_path = self._cfg.get_index_file_path(
                path=self._cfg.TMP_UPLOAD_FRAME_DIR,
                id=sign_id,
                index=idx,
                ext=".jpg",
                mkdir=True,
            )

            if frame_path is None:
                msg = f"could not resolve frame path: {idx}"
                self._logger.error(
                    message=msg, module="VideoPipeline.upload_sign_video"
                )
                raise ValueError(msg)

            ok = cv2.imwrite(str(frame_path), frame)
            if not ok:
                msg = f"could not save frame: {frame_path}"
                self._logger.error(
                    message=msg, module="VideoPipeline.upload_sign_video"
                )
                raise ValueError(msg)

            frame_paths.append(str(frame_path))
            idx += 1

        cap.release()

        gallery_items = [(path, str(i)) for i, path in enumerate(frame_paths, start=1)]

        return sign_id, fps, gallery_items, len(frame_paths)

from pathlib import Path

import gradio as gr

from src.engine.preprocess.dataset_io import DatasetIO
from src.engine.preprocess.smplx_estimator import SMPLXEstimator

# from gradio.routes import App
from src.engine.preprocess.video_pipeline import VideoPipeline
from src.utils.config import AppConfig
from src.utils.logger import Logger


class PreprocessController:
    def __init__(self) -> None:
        self._cfg = AppConfig()
        self._logger = Logger()
        self._video_pipeline = VideoPipeline()
        self._smplx_estimator = SMPLXEstimator()
        self._dataset_io = DatasetIO()

    def sign_video_change(self):
        return (
            gr.update(value=None),
            gr.update(value=None),
            gr.update(value=None),
            gr.update(value=None),
            gr.update(value=None),
            gr.update(value=None),
            gr.update(value=None),
        )

    def upload_sign_video_controller(
        self, filepath: str
    ) -> tuple[str, float, list[tuple[str, str]], int]:
        try:
            vid, fps, gallery, num_frames = self._video_pipeline.upload_sign_video(
                upload_file=filepath
            )
            return vid, fps, gallery, num_frames

        except ValueError as e:
            gr.Warning(str(e))
            return "", 0, [], 0

    def reconstruct_mesh_human_controller(
        self,
        video_id: str,
        frame_rate: int,
    ) -> Path | None:

        if not video_id:
            gr.Warning("Please provide a valid video ID.")
            return None

        if frame_rate is None or frame_rate <= 0:
            gr.Warning("Frame rate must be greater than 0.")
            return None

        try:
            filepath = self._smplx_estimator.smplx_estimator(
                video_id=video_id,
                frame_rate=frame_rate,
            )

            if filepath and filepath.exists():
                return filepath

            gr.Warning("Mesh reconstruction completed, but output file was not found.")
            return None

        except Exception as e:
            gr.Error(f"Unexpected error during mesh reconstruction: {e}")

        return None

    def save_data_controller(
        self,
        vid: str,
        gloss: str,
        frame_rate: int,
        num_frames: int,
        frame_start: int,
        frame_end: int,
        # viz_video,
    ) -> None:
        try:
            if vid == "":
                gr.Warning("video is empty")
                return None

            if frame_start is None or frame_end is None:
                gr.Warning("frame_start,frame_end is empty")
                return None

            if gloss == "":
                gr.Warning("Gloss fields or mesh is empty")
                return None

            self._dataset_io.save_to_dataset(
                video_id=vid,
                gloss=gloss,
                frame_rate=frame_rate,
                num_frames=num_frames,
                frame_start=frame_start,
                frame_end=frame_end,
            )

            gr.Info("✅ Save to dataset success")

        except Exception as e:
            gr.Error(f"Unexpected error during mesh reconstruction: {e}")

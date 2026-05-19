import gradio as gr

from src.engine.preprocess.video_pipeline import VideoPipeline
from src.utils.logger import Logger


class PreprocessController:
    def __init__(self) -> None:
        self._logger = Logger()
        self._video_pipeline = VideoPipeline()

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

    def reconstruct_mesh_human_controller(self, vid, fps):
        pass
        # if vid is None or fps is None:
        #     gr.Warning(ERROR_MESSAGES[ErrorCode.INVALID_INPUT])
        #     return

        # result = ReconstructService.reconstruct_mesh_human(video_id=vid, frame_rate=fps)

        # if result.success:
        #     return result.data

        # else:
        #     gr.Warning(result.message)

    def save_data_controller(
        self, vid, gloss, fps, num_frames, frame_start, frame_end, viz_video
    ):
        pass
        # if vid == "":
        #     gr.Warning(f"video is empty")
        #     return

        # if frame_start is None or frame_end is None:
        #     gr.Warning(f"frame_start,frame_end is empty")
        #     return

        # if gloss == "":
        #     gr.Warning(f"Gloss fields or mesh is empty")
        #     return

        # result = DatasetService.save_to_dataset(
        #     video_id=vid,
        #     gloss=gloss,
        #     fps=fps,
        #     num_frames=num_frames,
        #     frame_start=frame_start,
        #     frame_end=frame_end,
        # )

        # if result.success:
        #     gr.Info(result.message)

        # else:
        #     gr.Warning(f"⚠️ {result.message}")

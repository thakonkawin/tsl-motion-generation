import time
from typing import Any

import gradio as gr

from src.engine.preprocess.dataset_io import DatasetIO
from src.utils.config import AppConfig
from src.utils.logger import Logger


class Text2MotionController:
    def __init__(self) -> None:
        self._cfg = AppConfig()
        self._logger = Logger()
        self._dataset_io = DatasetIO()

    def generate_tsl_controller(self, text_input: str) -> str | None:

        if text_input == "":
            gr.Warning("text is empty")
            return None

        progress = gr.Progress()
        total_frames = 100

        for i in range(total_frames):
            time.sleep(0.05)

            percent = (i + 1) / total_frames

            progress(percent, desc=f"Rendering .... {i + 1}/{total_frames} frame")

        return "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4"

        # start = time.time()
        # cleaned_text = text_input.strip()

        # glosses = cleaned_text.split()

        # # result_query = DatasetService.search_gloss_sequence(glosses=glosses)
        # # if not result_query.success:
        # #     raise gr.Error(result_query.message)

        # # result = RenderService.render_sentence(df=result_query.data)
        # # if not result.success:
        # #     raise gr.Error(result.message)

        # elapsed = time.time() - start
        # message = f"Time Redering: {elapsed / 60:.2f} นาที"
        # self._logger.success(
        #     message=message, module="SentenceController.generate_tsl_controller"
        # )

        # return result.data, cleaned_text
        #
        #

    def on_video_change_controller(
        self, motion_path: str, sentence: str
    ) -> tuple[list[tuple[Any, Any]], str] | None:
        try:
            data = self._dataset_io.add_motion_recent(
                motion_path=motion_path, sentence=sentence
            )
            sorted_recents = sorted(
                data.get("recents", []),
                key=lambda x: x.get("created_at", ""),
                reverse=True,
            )
            return [
                (item["video_path"], item["sentence"]) for item in sorted_recents
            ], sentence
        except Exception as e:
            gr.Warning(message=f"on_video_change_controller: {e}")

    def get_recent_controller(self) -> list[tuple[Any, Any]] | None:
        try:
            data = self._dataset_io.load_json()

            sorted_recents = sorted(
                data.get("recents", []),
                key=lambda x: x.get("created_at", ""),
                reverse=True,
            )
            return [(item["video_path"], item["sentence"]) for item in sorted_recents]
        except Exception as e:
            gr.Warning(message=f"get_recent_controller: {e}")

    def add_recent_controller(
        self, motion_path: str, sentence: str
    ) -> list[tuple[Any, Any]] | None:
        try:
            data = self._dataset_io.add_motion_recent(
                motion_path=motion_path, sentence=sentence
            )
            sorted_recents = sorted(
                data.get("recents", []),
                key=lambda x: x.get("created_at", ""),
                reverse=True,
            )
            return [(item["video_path"], item["sentence"]) for item in sorted_recents]
        except Exception as e:
            gr.Warning(message=f"add_recent_controller: {e}")

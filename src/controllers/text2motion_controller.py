import time
import traceback
from pathlib import Path
from typing import Any

import gradio as gr

from src.engine.generations.motion_generator import MotionGenerator
from src.engine.language.retrieval import LanguageRetrieval
from src.engine.preprocess.dataset_io import DatasetIO
from src.engine.preprocess.video_pipeline import VideoPipeline
from src.engine.visualizations.renderer import Renderer
from src.utils.config import AppConfig
from src.utils.logger import Logger


class Text2MotionController:
    def __init__(self) -> None:
        self._cfg = AppConfig()
        self._logger = Logger()
        self._dataset_io = DatasetIO()
        self._motion_generator = MotionGenerator()
        self._lang_retrieval = LanguageRetrieval()
        self._video_pipeline = VideoPipeline()

    def generate_tsl_controller(
        self, text_input: str, progress=gr.Progress()
    ) -> Path | None:

        try:
            start = time.time()
            self._logger.info(f"Retrieving glosses... {text_input}")

            progress(0.1, desc="Retrieving glosses...")
            gloss_sequence = self._lang_retrieval.retrieve_glosses(
                text_input=text_input
            )

            if gloss_sequence.empty:
                msg = f"Gloss sequence is empty {text_input}"
                self._logger.error(
                    msg, module="generate_tsl_controller.retrieve_glosses"
                )
                gr.Error(message=msg)

            progress(0.2, desc="Generating motion...")
            motion_list, motion_id, frame_rate, _ = (
                self._motion_generator.generate_sentence_motion(
                    gloss_sequence=gloss_sequence, gender="neutral"
                )
            )

            if len(motion_list) > 0:
                self._logger.info(f"first motion={motion_list[0]}")

            progress(0.3, desc="Starting render...")
            renderer = Renderer(
                motion_id=motion_id,
                motion_list=motion_list,
                resolution=(512, 512),
            )
            renderer.run(
                sign_id=motion_id,
                target_path=self._cfg.TMP_MOTION_SENTENCE_DIR,
                progress=progress,
            )

            progress(0.95, desc="Converting to video...")
            output_path = self._video_pipeline.images_to_video(
                motion_id=motion_id,
                frame_rate=frame_rate,
            )

            if output_path is None:
                self._logger.error("Video generation failed")
                gr.Error(message="Video generation failed")
                return None

            progress(1.0, desc="Done!")
            elapsed = time.time() - start
            render_time = f"Time Redering: {elapsed / 60:.2f} Minutes"
            self._logger.info(render_time)
            return output_path

        except Exception as e:
            self._logger.error(f"generate_tsl_controller error: {e!r}")
            self._logger.error(traceback.format_exc())
            gr.Error(message=str(e))

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

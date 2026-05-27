import time
from pathlib import Path

import gradio as gr
import pandas as pd

from src.engine.generations.motion_generator import MotionGenerator
from src.engine.preprocess.dataset_io import DatasetIO
from src.engine.preprocess.video_pipeline import VideoPipeline
from src.engine.visualizations.renderer import Renderer
from src.utils.config import AppConfig
from src.utils.logger import Logger


class DatasetController:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()
        self._dataset_io = DatasetIO()
        self._motion_generator = MotionGenerator()
        self._video_pipeline = VideoPipeline()

    def on_select_word(self, table_df, evt: gr.SelectData) -> tuple[str, str, int, int]:

        if isinstance(table_df, pd.DataFrame):
            df = table_df
        else:
            df = pd.DataFrame(table_df)

        row = df.iloc[evt.index[0]]

        return (
            str(row["sign_id"]),
            str(row["gloss"]),
            int(row["frame_rate"]),
            int(row["num_frames"]),
        )

    def get_metadata_controller(self) -> pd.DataFrame | None:
        try:
            return self._dataset_io.load_metadata()

        except Exception as e:
            gr.Warning(message=f"get_metadata_controller: {e}")

    def refresh_data_controller(self) -> tuple[str, pd.DataFrame] | None:
        df = self.get_metadata_controller()

        if df is not None:
            return (str(len(df)), df)

        return None

    def delete_data_controller(self, sign_id: str):
        try:
            return self._dataset_io.delete_metadata(sign_id=sign_id)

        except Exception as e:
            gr.Error(message=f"delete_data_controller: {e}")

    def compute_mesh_controller(
        self, sign_id: str, frame_rate: int, num_frames: int, progress=gr.Progress()
    ) -> Path | None:

        try:
            start = time.time()
            progress(0.1, desc="Generating motion...")
            motion_list = self._motion_generator.generate_gloss_motion(
                motion_id=sign_id, num_frames=num_frames, gender="neutral"
            )

            progress(0.3, desc="Starting render...")
            renderer = Renderer(
                motion_id=sign_id,
                motion_list=motion_list,
                resolution=(512, 512),
            )
            renderer.run(
                sign_id=sign_id,
                target_path=self._cfg.TMP_MOTION_GLOSS_DIR,
                progress=progress,
            )

            progress(0.95, desc="Converting to video...")
            ouput_path = self._video_pipeline.images_to_video(
                motion_id=sign_id, frame_rate=frame_rate
            )

            self._logger.info("Done!")
            progress(1.0, desc="Done!")
            elapsed = time.time() - start
            render_time = f"Time Redering: {elapsed / 60:.2f} Minutes"
            self._logger.info(render_time)
            return ouput_path

        except Exception as e:
            gr.Warning(message=f"compute_mesh_controller: {e}")
            return None

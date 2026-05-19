# from logging import exception

import gradio as gr
import pandas as pd

from src.engine.preprocess.dataset_io import DatasetIO
from src.utils.logger import Logger


class DatasetController:
    def __init__(self) -> None:
        self._logger = Logger()
        self._dataset_io = DatasetIO()

    def on_select_word(self, table_df, evt: gr.SelectData) -> tuple[str, str, int, int]:

        if isinstance(table_df, pd.DataFrame):
            df = table_df
        else:
            df = pd.DataFrame(table_df)

        row = df.iloc[evt.index[0]]

        return (
            str(row["sign_id"]),
            str(row["gloss"]),
            int(row["fps"]),
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

    def compute_mesh_controller(self, sign_id, fps, num_frames):
        pass
        # if sign_id is None or fps is None or num_frames is None:
        #     gr.Warning("Please select a sign before computing")

        # result = RenderService.render_gloss(sign_id, fps, num_frames)
        # if not result.success:
        #     gr.Warning(result.error_code)

        # return result.data

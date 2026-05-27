import uuid
from typing import cast

import h5py
import numpy as np
import pandas as pd

from src.engine.preprocess.dataset_io import DatasetIO
from src.utils.config import AppConfig
from src.utils.logger import Logger


class MotionGenerator:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()
        self._dataset_io = DatasetIO()

    def generate_gloss_motion(
        self, motion_id: str, num_frames: int, gender: str
    ) -> list:
        try:
            motion_data = self._dataset_io.load_motion_data(sign_id=motion_id)

            group = cast(h5py.Group, motion_data[motion_id])
            vertices_group = cast(h5py.Group, group["vertices"])

            motion_paths = []
            for idx in range(num_frames):
                smplx_params = {}

                for param_name in vertices_group.keys():
                    data = cast(h5py.Dataset, vertices_group[param_name])
                    param_data = np.asarray(data[idx])
                    param_data = np.expand_dims(param_data, axis=0)

                    smplx_params[param_name] = param_data
                    smplx_params["gender"] = gender

                    motion_path = self._cfg.get_index_file_path(
                        path=self._cfg.TMP_MOTION_GLOSS_DIR,
                        id=motion_id,
                        index=idx,
                        ext=".pkl",
                        mkdir=True,
                    )

                    self._dataset_io.dump_pkl(motion_path, smplx_params)
                    motion_paths.append(motion_path)

            return motion_paths

        except Exception as e:
            self._logger.error(
                message=str(e), module="MotionGenerator.generate_gloss_motion"
            )
            raise RuntimeError(str(e))

    def _set_frame_transition(self, data: pd.DataFrame) -> pd.DataFrame:
        if not data.empty:
            data.loc[0, "frame_start"] = 1
            data.loc[data.index[-1], "frame_end"] = data.iloc[-1]["num_frames"]

            data["num_frames"] = (data["frame_end"] - data["frame_start"] + 1).astype(
                int
            )

        return data

    def generate_sentence_motion(
        self, gloss_sequence: pd.DataFrame, gender: str
    ) -> tuple[list, str, int, int]:

        motions = self._set_frame_transition(data=gloss_sequence)

        motion_id = str(uuid.uuid4())

        motion_paths = []
        frame_rate = 0
        frame_number = 0

        for _, row in motions.iterrows():
            sign_id = str(row["sign_id"])

            motion_data = self._dataset_io.load_motion_data(sign_id=sign_id)

            group = cast(h5py.Group, motion_data[sign_id])
            vertices_group = cast(h5py.Group, group["vertices"])

            start_frame = cast(int, row["frame_start"])
            end_frame = cast(int, row["frame_end"])
            frame_rate = cast(int, row["frame_rate"])

            for frame_idx in range(start_frame, end_frame):
                smplx_params = {}

                for param_name in vertices_group.keys():
                    data = cast(h5py.Dataset, vertices_group[param_name])

                    param_data = np.asarray(data[frame_idx])
                    param_data = np.expand_dims(param_data, axis=0)

                    smplx_params[param_name] = param_data

                smplx_params["gender"] = gender

                motion_path = self._cfg.get_index_file_path(
                    path=self._cfg.TMP_MOTION_SENTENCE_DIR,
                    id=motion_id,
                    index=frame_number,
                    ext=".pkl",
                    mkdir=True,
                )

                self._dataset_io.dump_pkl(motion_path, smplx_params)

                motion_paths.append(motion_path)

                frame_number += 1

        return motion_paths, motion_id, frame_rate, frame_number

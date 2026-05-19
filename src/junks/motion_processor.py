import uuid
from typing import cast

import h5py
import pandas as pd

from core.processors.interfaces.motion_interface import MotionInterface
from core.utils.config import AppConfig
from core.utils.logger import Logger


class MotionProcessor(MotionInterface):
    def __init__(self, model_path: str) -> None:
        self._model_path = model_path
        self._logger = Logger()

    def _set_frame_transition(self, data: pd.DataFrame) -> pd.DataFrame:
        if not data.empty:
            data.loc[0, "frame_start"] = 1
            data.loc[data.index[-1], "frame_end"] = data.iloc[-1]["num_frames"]

            data["num_frames"] = (data["frame_end"] - data["frame_start"] + 1).astype(
                int
            )

        return data

    def generate_sentence_motion(self, gloss_sequence: pd.DataFrame) -> None:

        motion_data = self._set_frame_transition(data=gloss_sequence)

        motion_id = str(uuid.uuid4())

        motion_folder = AppConfig.ROOT_DIR / AppConfig.MOTION_SENTENCE_DIR
        motion_folder.mkdir(parents=True, exist_ok=True)

        frame_number = 0

        with h5py.File(AppConfig.ROOT_DIR / AppConfig.DATASET_PATH, "r") as f:
            for _, row in motion_data.iterrows():
                sign_id = str(row["sign_id"])

                group = cast(h5py.Group, f[sign_id])

                vertices_group = group["vertices"]

                start_frame = cast(int, row["frame_start"])
                end_frame = cast(int, row["frame_end"])
                frame_rate = cast(int, row["fps"])
                # loop ตามช่วง START-END
                for frame_idx in range(start_frame, end_frame):
                    smplx_params = {}

                    for param_name in vertices_group.keys():
                        # ใช้ frame เดียวกันทุก param
                        param_data = vertices_group[param_name][frame_idx]

                        param_data = np.expand_dims(param_data, axis=0)

                        smplx_params[param_name] = param_data

                    smplx_params["gender"] = "neutral"

                    motion_path = PathManager.get_motion_path(motion_id, frame_number)

                    dump_pkl(motion_path, smplx_params)

                    frame_number += 1

        result = [motion_id, frame_rate, frame_number]

        return result

        # pass
        # try:
        #     data = MotionService.set_frame_transition(df=df)

        #     motion_id = str(uuid.uuid4())

        #     motion_folder = PathManager.get_motion_dir(motion_id)
        #     motion_folder.mkdir(parents=True, exist_ok=True)

        #     frame_number = 0

        #     with h5py.File(PathManager.TSL_H5_PATH, "r") as f:

        #         for _, row in data.iterrows():

        #             print(f"sign_id for motion: {row['sign_id']}")

        #             vertices_group = f[row["sign_id"]]["vertices"]

        #             start_frame = int(row["frame_start"]) - 1
        #             end_frame = int(row["frame_end"])  # python range ไม่รวมตัวท้าย
        #             frame_rate = int(row["fps"])

        #             # loop ตามช่วง START-END
        #             for frame_idx in range(start_frame, end_frame):

        #                 smplx_params = {}

        #                 for param_name in vertices_group.keys():

        #                     # ใช้ frame เดียวกันทุก param
        #                     param_data = vertices_group[param_name][frame_idx]

        #                     param_data = np.expand_dims(param_data, axis=0)

        #                     smplx_params[param_name] = param_data

        #                 smplx_params["gender"] = "neutral"

        #                 motion_path = PathManager.get_motion_path(
        #                     motion_id, frame_number
        #                 )

        #                 dump_pkl(motion_path, smplx_params)

        #                 frame_number += 1

        #     result = [motion_id, frame_rate, frame_number]

        #     return success_result(data=result)

        # except Exception as e:
        #     return error_result(
        #         ErrorCode.UNKNOWN_ERROR,
        #         message=f"create_sentence_motion: {e}",
        #     )

import uuid

import h5py
import numpy as np
import pandas as pd
from src.utils.files import dump_pkl
from src.utils.path_manager import PathManager
from src.utils.result import error_result, success_result
from src.const.errors import ErrorCode


from src.utils.path_manager import PathManager

PathManager.ensure_dirs()


class MotionService:

    @staticmethod
    def create_gloss_motion(motion_id, num_frames, gender):
        try:
            with h5py.File(PathManager.TSL_H5_PATH, "r") as f:

                if motion_id not in f:
                    return error_result(
                        ErrorCode.MOTION_CREATE_FAILED,
                        message=f"Motion ID '{motion_id}' not found in H5 file",
                    )

                vertices_group = f[motion_id]["vertices"]

                motion_folder = PathManager.get_motion_dir(motion_id)
                motion_folder.mkdir(parents=True, exist_ok=True)

                for idx in range(num_frames):

                    smplx_params = {}

                    for param_name in vertices_group.keys():

                        param_data = vertices_group[param_name][idx]

                        # add batch dimension back
                        param_data = np.expand_dims(param_data, axis=0)

                        smplx_params[param_name] = param_data

                    smplx_params["gender"] = gender

                    motion_path = PathManager.get_motion_path(motion_id, idx)

                    dump_pkl(motion_path, smplx_params)

            return success_result()

        except Exception as e:
            return error_result(
                ErrorCode.UNKNOWN_ERROR, message=f"create_gloss_motion: {e}"
            )

    @staticmethod
    def set_frame_transition(df: pd.DataFrame):
        if not df.empty:
            df.loc[0, "frame_start"] = 1
            df.loc[df.index[-1], "frame_end"] = df.iloc[-1]["num_frames"]

            df["num_frames"] = (df["frame_end"] - df["frame_start"] + 1).astype(int)

        return df

    @staticmethod
    def create_sentence_motion(df: pd.DataFrame):

        try:
            data = MotionService.set_frame_transition(df=df)

            motion_id = str(uuid.uuid4())

            motion_folder = PathManager.get_motion_dir(motion_id)
            motion_folder.mkdir(parents=True, exist_ok=True)

            frame_number = 0

            with h5py.File(PathManager.TSL_H5_PATH, "r") as f:

                for _, row in data.iterrows():

                    print(f"sign_id for motion: {row['sign_id']}")

                    vertices_group = f[row["sign_id"]]["vertices"]

                    start_frame = int(row["frame_start"]) - 1
                    end_frame = int(row["frame_end"])  # python range ไม่รวมตัวท้าย
                    frame_rate = int(row["fps"])

                    # loop ตามช่วง START-END
                    for frame_idx in range(start_frame, end_frame):

                        smplx_params = {}

                        for param_name in vertices_group.keys():

                            # ใช้ frame เดียวกันทุก param
                            param_data = vertices_group[param_name][frame_idx]

                            param_data = np.expand_dims(param_data, axis=0)

                            smplx_params[param_name] = param_data

                        smplx_params["gender"] = "neutral"

                        motion_path = PathManager.get_motion_path(
                            motion_id, frame_number
                        )

                        dump_pkl(motion_path, smplx_params)

                        frame_number += 1

            result = [motion_id, frame_rate, frame_number]

            return success_result(data=result)

        except Exception as e:
            return error_result(
                ErrorCode.UNKNOWN_ERROR,
                message=f"create_sentence_motion: {e}",
            )

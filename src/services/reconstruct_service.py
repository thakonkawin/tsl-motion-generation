# import pandas as
import os
import cv2
import h5py
import uuid
import shutil
import subprocess
import numpy as np
import pandas as pd
from src.utils.files import load_pkl
from src.utils.path_manager import PathManager
from src.utils.result import Result, error_result, success_result
from src.const.errors import ErrorCode


from src.utils.path_manager import PathManager

PathManager.ensure_dirs()


class ReconstructService:

    @staticmethod
    def reconstruct_mesh_human(video_id, frame_rate) -> Result:

        script_path = PathManager.INFERENCE_SMPLESTX_SCRIPT
        vid_path = PathManager.get_upload_video_path(video_id)

        cmd = ["bash", script_path, "smplest_x_h", vid_path, str(frame_rate)]

        try:

            subprocess.run(cmd, check=True)

            result_path = PathManager.get_tmp_mesh_video_path(video_id)
            if not os.path.exists(result_path):
                return error_result(ErrorCode.RECONSTRUCT_FAILED)

            return success_result(data=result_path)

        except Exception as e:
            return error_result(
                ErrorCode.UNKNOWN_ERROR, message=f"reconstruct_3d_human: {e}"
            )

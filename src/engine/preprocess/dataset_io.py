import pickle
from pathlib import Path
from typing import Any

import h5py
import pandas as pd

from src.utils.config import AppConfig
from src.utils.logger import Logger


class DatasetIO:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def load_metadata(self) -> pd.DataFrame:
        filepath = self._cfg.get_path(self._cfg.METADATA_PATH)
        if not filepath.exists():
            msg = f"could not resolve csv path {filepath}"
            self._logger.error(message=msg, module="DatasetIO.load_metadata")
            raise ValueError(msg)

        return pd.read_csv(filepath)

    def delete_metadata(self, sign_id: str) -> None:

        df = self.load_metadata()

        if "sign_id" not in df.columns:
            raise KeyError("Missing 'sign_id' column in metadata")

        before_count = len(df)

        filtered_df = df[df["sign_id"].astype(str) != sign_id]

        if len(filtered_df) == before_count:
            msg = f"sign_id '{sign_id}' not found in metadata"
            self._logger.error(message=msg, module="DatasetIO.delete_metadata")
            raise ValueError(msg)

        file_csv = self._cfg.get_path(self._cfg.METADATA_PATH)
        file_h5 = self._cfg.get_path(self._cfg.DATASET_PATH)

        try:
            # Save metadata
            filtered_df.to_csv(file_csv, index=False)

            # Delete HDF5 dataset
            if file_h5.exists():
                with h5py.File(file_h5, "a") as h5f:
                    if sign_id in h5f:
                        del h5f[sign_id]
                    else:
                        self._logger.warn(
                            message=f"sign_id '{sign_id}' not found in HDF5",
                            module="DatasetIO.delete_metadata",
                        )

        except Exception as e:
            self._logger.error(
                message=str(e),
                module="DatasetIO.delete_metadata",
            )
            raise FileNotFoundError(str(e))

    def load_motion_data(self, sign_id: str) -> h5py.File:
        file_h5 = self._cfg.get_path(self._cfg.DATASET_PATH)

        try:
            if not file_h5.exists():
                raise FileNotFoundError(f"HDF5 file not found: {file_h5}")

            h5f = h5py.File(file_h5, "r")

            if sign_id not in h5f:
                h5f.close()

                msg = f"sign_id '{sign_id}' not found in HDF5"

                self._logger.warn(
                    message=msg,
                    module="DatasetIO.load_motion_data",
                )

                raise ValueError(msg)

            return h5f

        except Exception as e:
            self._logger.error(
                message=str(e),
                module="DatasetIO.load_motion_data",
            )
            raise RuntimeError(str(e))

    def dump_pkl(self, path: Path | str, data: Any) -> None:
        with open(path, "wb") as f:
            pickle.dump(data, f)

    # def _save_vertices(paths, video_id):

    #     try:
    #         # Collect parameter data
    #         global_orient = []
    #         body_pose = []
    #         left_hand_pose = []
    #         right_hand_pose = []
    #         jaw_pose = []
    #         leye_pose = []
    #         reye_pose = []
    #         transl = []
    #         betas = []
    #         expression = []

    #         for pkl_path in paths:
    #             data = load_pkl(pkl_path)

    #             global_orient.append(data["global_orient"][0])
    #             body_pose.append(data["body_pose"][0])
    #             left_hand_pose.append(data["left_hand_pose"][0])
    #             right_hand_pose.append(data["right_hand_pose"][0])
    #             jaw_pose.append(data["jaw_pose"][0])
    #             leye_pose.append(data["leye_pose"][0])
    #             reye_pose.append(data["reye_pose"][0])
    #             transl.append(data["transl"][0])
    #             betas.append(data["betas"][0])
    #             expression.append(data["expression"][0])

    #         # Convert to numpy
    #         global_orient = np.asarray(global_orient, dtype=np.float32)
    #         body_pose = np.asarray(body_pose, dtype=np.float32)
    #         left_hand_pose = np.asarray(left_hand_pose, dtype=np.float32)
    #         right_hand_pose = np.asarray(right_hand_pose, dtype=np.float32)
    #         jaw_pose = np.asarray(jaw_pose, dtype=np.float32)
    #         leye_pose = np.asarray(leye_pose, dtype=np.float32)
    #         reye_pose = np.asarray(reye_pose, dtype=np.float32)
    #         transl = np.asarray(transl, dtype=np.float32)
    #         betas = np.asarray(betas, dtype=np.float32)
    #         expression = np.asarray(expression, dtype=np.float32)

    #         # Save to HDF5
    #         h5_path = PathManager.TSL_H5_PATH
    #         with h5py.File(h5_path, "a") as h5f:
    #             # overwrite old vid
    #             if video_id in h5f:
    #                 del h5f[video_id]

    #             sample_group = h5f.create_group(video_id)

    #             # Vertice Group
    #             vt_group = sample_group.create_group("vertices")
    #             vt_group.create_dataset("betas", data=betas)
    #             vt_group.create_dataset("global_orient", data=global_orient)
    #             vt_group.create_dataset("body_pose", data=body_pose)
    #             vt_group.create_dataset("left_hand_pose", data=left_hand_pose)
    #             vt_group.create_dataset("right_hand_pose", data=right_hand_pose)
    #             vt_group.create_dataset("jaw_pose", data=jaw_pose)
    #             vt_group.create_dataset("leye_pose", data=leye_pose)
    #             vt_group.create_dataset("reye_pose", data=reye_pose)
    #             vt_group.create_dataset("transl", data=transl)
    #             vt_group.create_dataset("expression", data=expression)

    #         return success_result()

    #     except Exception as e:
    #         return error_result(ErrorCode.UNKNOWN_ERROR, message=f"_save_vertices: {e}")

    # @staticmethod
    # def _save_csv(
    #     path: str,
    #     video_id: str,
    #     gloss: str,
    #     fps: float,
    #     num_frames: int,
    #     frame_start: int,
    #     frame_end: int,
    # ):

    #     row = {
    #         "sign_id": video_id,
    #         "gloss": gloss,
    #         "fps": fps,
    #         "num_frames": num_frames,
    #         "frame_start": frame_start,
    #         "frame_end": frame_end,
    #     }

    #     try:
    #         file_exists = os.path.exists(path) and os.path.getsize(path) > 0

    #         if file_exists:
    #             try:
    #                 df = pd.read_csv(path)
    #                 df = df[df["sign_id"] != video_id]
    #                 df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    #             except pd.errors.EmptyDataError:
    #                 df = pd.DataFrame([row])
    #         else:
    #             df = pd.DataFrame([row])

    #         df.to_csv(path, index=False)
    #         return success_result()

    #     except Exception as e:
    #         return error_result(ErrorCode.UNKNOWN_ERROR, message=f"_save_csv: {e}")

    # @staticmethod
    # def _rollback_vertices(video_id):
    #     with h5py.File(PathManager.TSL_H5_PATH, "a") as h5f:
    #         if video_id in h5f:
    #             del h5f[video_id]

    # @staticmethod
    # def _rollback_keypoints(video_id):
    #     with h5py.File(PathManager.TSL_H5_PATH, "a") as h5f:
    #         if video_id in h5f:
    #             del h5f[video_id]

    # @staticmethod
    # def _rollback_csv(video_id):
    #     path = PathManager.METADATA_PATH
    #     if not path.exists():
    #         return

    #     df = pd.read_csv(path)
    #     df = df[df["sign_id"] != video_id]
    #     df.to_csv(path, index=False)

    # @staticmethod
    # def save_to_dataset(
    #     video_id,
    #     gloss,
    #     fps,
    #     num_frames,
    #     frame_start,
    #     frame_end,
    # ):

    #     tx = TransactionManager()

    #     try:
    #         # Find files
    #         pkl_paths = PathManager.get_tmp_smplx_pkl_paths(video_id)
    #         # kp_paths = (PathManager.get_tmp_keypoint_json_paths(video_id))
    #         # if not pkl_paths or not kp_paths:
    #         #     return False, "⚠️ No dataset files"

    #         # # Save keypoints
    #         # keypoint_result = _save_keypoints(paths=kp_paths, video_id=video_id)
    #         # if not keypoint_result.success:
    #         #     tx.rollback()
    #         # return error_result(keypoint_result.error_code, keypoint_result.message)

    #         # tx.add_rollback(_rollback_keypoints, video_id)

    #         # Save vertices
    #         vertice_result = DatasetService._save_vertices(
    #             paths=pkl_paths, video_id=video_id
    #         )
    #         if not vertice_result.success:
    #             tx.rollback()
    #             return error_result(vertice_result.error_code, vertice_result.message)

    #         tx.add_rollback(DatasetService._rollback_vertices, video_id)

    #         csv_path = str(PathManager.METADATA_PATH)

    #         # Save CSV
    #         csv_result = DatasetService._save_csv(
    #             path=csv_path,
    #             video_id=video_id,
    #             gloss=gloss,
    #             fps=fps,
    #             num_frames=num_frames,
    #             frame_start=frame_start,
    #             frame_end=frame_end,
    #         )

    #         if not csv_result.success:
    #             tx.rollback()
    #             return error_result(csv_result.error_code, csv_result.message)

    #         tx.add_rollback(DatasetService._rollback_csv, video_id)

    #         # Success
    #         return success_result(message="✅ Save dataset success")

    #     except Exception as e:
    #         tx.rollback()
    #         return error_result(
    #             ErrorCode.UNKNOWN_ERROR, message=f"save_to_dataset: {e}"
    #         )

    # @staticmethod
    # def load_json():
    #     if not PathManager.RECENT_JSON_PATH.exists():
    #         return error_result(error_code=ErrorCode.INVALID_INPUT)

    #     with open(PathManager.RECENT_JSON_PATH, "r", encoding="utf-8") as f:
    #         data = json.load(f)

    #     return success_result(data=data)

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
from src.utils.transaction_manager import TransactionManager

PathManager.ensure_dirs()


DF_HEADERS = [
    "sign_id",
    "gloss",
    "fps",
    "num_frames",
    "frame_start",
    "frame_end",
]


class DatasetService:

    @staticmethod
    def upload_sign_video(upload_file) -> Result:
        try:
            vid = str(uuid.uuid4())

            # create path
            frame_paths = []
            video_path = PathManager.get_upload_video_path(vid)
            frame_folder = PathManager.get_upload_frame_dir(vid)
            frame_folder.mkdir(parents=True, exist_ok=True)

            # save upload video
            shutil.copy(upload_file, video_path)

            # extract upload frames
            cap = cv2.VideoCapture(video_path)

            # get upload frames
            fps = cap.get(cv2.CAP_PROP_FPS)

            idx = 1
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_path = PathManager.get_upload_frame_path(vid, idx)
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                idx += 1

            cap.release()

            gallery_items = [
                (frame_path, str(idx))
                for idx, frame_path in enumerate(frame_paths, start=1)
            ]

            data = [vid, fps, gallery_items, len(frame_paths)]
            return success_result(data=data)

        except Exception as e:
            return error_result(
                ErrorCode.INVALID_INPUT, message=f"upload_sign_video: {e}"
            )

    @staticmethod
    def _save_keypoints(paths, video_id):
        pass

    @staticmethod
    def _save_vertices(paths, video_id):

        try:
            # Collect parameter data
            global_orient = []
            body_pose = []
            left_hand_pose = []
            right_hand_pose = []
            jaw_pose = []
            leye_pose = []
            reye_pose = []
            transl = []
            betas = []
            expression = []

            for pkl_path in paths:
                data = load_pkl(pkl_path)

                global_orient.append(data["global_orient"][0])
                body_pose.append(data["body_pose"][0])
                left_hand_pose.append(data["left_hand_pose"][0])
                right_hand_pose.append(data["right_hand_pose"][0])
                jaw_pose.append(data["jaw_pose"][0])
                leye_pose.append(data["leye_pose"][0])
                reye_pose.append(data["reye_pose"][0])
                transl.append(data["transl"][0])
                betas.append(data["betas"][0])
                expression.append(data["expression"][0])

            # Convert to numpy
            global_orient = np.asarray(global_orient, dtype=np.float32)
            body_pose = np.asarray(body_pose, dtype=np.float32)
            left_hand_pose = np.asarray(left_hand_pose, dtype=np.float32)
            right_hand_pose = np.asarray(right_hand_pose, dtype=np.float32)
            jaw_pose = np.asarray(jaw_pose, dtype=np.float32)
            leye_pose = np.asarray(leye_pose, dtype=np.float32)
            reye_pose = np.asarray(reye_pose, dtype=np.float32)
            transl = np.asarray(transl, dtype=np.float32)
            betas = np.asarray(betas, dtype=np.float32)
            expression = np.asarray(expression, dtype=np.float32)

            # Save to HDF5
            h5_path = PathManager.TSL_H5_PATH
            with h5py.File(h5_path, "a") as h5f:

                # overwrite old vid
                if video_id in h5f:
                    del h5f[video_id]

                sample_group = h5f.create_group(video_id)

                # Vertice Group
                vt_group = sample_group.create_group("vertices")
                vt_group.create_dataset("betas", data=betas)
                vt_group.create_dataset("global_orient", data=global_orient)
                vt_group.create_dataset("body_pose", data=body_pose)
                vt_group.create_dataset("left_hand_pose", data=left_hand_pose)
                vt_group.create_dataset("right_hand_pose", data=right_hand_pose)
                vt_group.create_dataset("jaw_pose", data=jaw_pose)
                vt_group.create_dataset("leye_pose", data=leye_pose)
                vt_group.create_dataset("reye_pose", data=reye_pose)
                vt_group.create_dataset("transl", data=transl)
                vt_group.create_dataset("expression", data=expression)

            return success_result()

        except Exception as e:
            return error_result(ErrorCode.UNKNOWN_ERROR, message=f"_save_vertices: {e}")

    @staticmethod
    def _save_csv(
        path: str,
        video_id: str,
        gloss: str,
        fps: float,
        num_frames: int,
        frame_start: int,
        frame_end: int,
    ):

        row = {
            "sign_id": video_id,
            "gloss": gloss,
            "fps": fps,
            "num_frames": num_frames,
            "frame_start": frame_start,
            "frame_end": frame_end,
        }

        try:
            file_exists = os.path.exists(path) and os.path.getsize(path) > 0

            if file_exists:
                try:
                    df = pd.read_csv(path)
                    df = df[df["sign_id"] != video_id]
                    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                except pd.errors.EmptyDataError:
                    df = pd.DataFrame([row])
            else:
                df = pd.DataFrame([row])

            df.to_csv(path, index=False)
            return success_result()

        except Exception as e:
            return error_result(ErrorCode.UNKNOWN_ERROR, message=f"_save_csv: {e}")

    @staticmethod
    def _rollback_vertices(video_id):
        with h5py.File(PathManager.TSL_H5_PATH, "a") as h5f:
            if video_id in h5f:
                del h5f[video_id]

    @staticmethod
    def _rollback_keypoints(video_id):
        with h5py.File(PathManager.TSL_H5_PATH, "a") as h5f:
            if video_id in h5f:
                del h5f[video_id]

    @staticmethod
    def _rollback_csv(video_id):
        path = PathManager.METADATA_PATH
        if not path.exists():
            return

        df = pd.read_csv(path)
        df = df[df["sign_id"] != video_id]
        df.to_csv(path, index=False)

    @staticmethod
    def save_to_dataset(
        video_id,
        gloss,
        fps,
        num_frames,
        frame_start,
        frame_end,
    ):

        tx = TransactionManager()

        try:
            # Find files
            pkl_paths = PathManager.get_tmp_smplx_pkl_paths(video_id)
            # kp_paths = (PathManager.get_tmp_keypoint_json_paths(video_id))
            # if not pkl_paths or not kp_paths:
            #     return False, "⚠️ No dataset files"

            # # Save keypoints
            # keypoint_result = _save_keypoints(paths=kp_paths, video_id=video_id)
            # if not keypoint_result.success:
            #     tx.rollback()
            # return error_result(keypoint_result.error_code, keypoint_result.message)

            # tx.add_rollback(_rollback_keypoints, video_id)

            # Save vertices
            vertice_result = DatasetService._save_vertices(
                paths=pkl_paths, video_id=video_id
            )
            if not vertice_result.success:
                tx.rollback()
                return error_result(vertice_result.error_code, vertice_result.message)

            tx.add_rollback(DatasetService._rollback_vertices, video_id)

            # Save CSV
            csv_result = DatasetService._save_csv(
                path=PathManager.METADATA_PATH,
                video_id=video_id,
                gloss=gloss,
                fps=fps,
                num_frames=num_frames,
                frame_start=frame_start,
                frame_end=frame_end,
            )

            if not csv_result.success:
                tx.rollback()
                return error_result(csv_result.error_code, csv_result.message)

            tx.add_rollback(DatasetService._rollback_csv, video_id)

            # Success
            return success_result(message="✅ Save dataset success")

        except Exception as e:
            tx.rollback()
            return error_result(
                ErrorCode.UNKNOWN_ERROR, message=f"save_to_dataset: {e}"
            )

    @staticmethod
    def load_metadata():
        if not PathManager.METADATA_PATH.exists():
            return error_result(error_code=ErrorCode.INVALID_INPUT)

        df = pd.read_csv(PathManager.METADATA_PATH)
        return success_result(data=df)

    @staticmethod
    def delete_metadata(sign_id):
        try:
            sign_id = str(sign_id)

            # Delete from metadata.csv
            if PathManager.METADATA_PATH.exists():
                df = pd.read_csv(PathManager.METADATA_PATH)

                before_count = len(df)
                df = df[df["sign_id"].astype(str) != sign_id]
                after_count = len(df)

                if before_count == after_count:
                    return error_result(error_code=ErrorCode.INDEX_OUT_OF_RANGE)

                df.to_csv(PathManager.METADATA_PATH, index=False)

            # Delete from tsl_dictionary.h5
            if PathManager.TSL_H5_PATH.exists():
                with h5py.File(PathManager.TSL_H5_PATH, "a") as h5f:

                    if sign_id in h5f:
                        del h5f[sign_id]

            return success_result(message="✅ Delete data success")

        except Exception as e:
            return error_result(
                ErrorCode.UNKNOWN_ERROR, message=f"delete_metadata: {e}"
            )

    @staticmethod
    def search_gloss_sequence(glosses):
        path = PathManager.METADATA_PATH
        if not path.exists():
            return

        df = pd.read_csv(path)

        # หา gloss ที่ไม่เจอ
        missing_glosses = [
            gloss for gloss in glosses if gloss not in set(df["gloss"].astype(str))
        ]

        # ต้องเจอทุกคำ
        if missing_glosses:
            return error_result(
                ErrorCode.METADATA_NOT_FOUND,
                message=f"Gloss not found: {missing_glosses}",
            )

        # reorder ตาม input
        ordered_rows = []

        for gloss in glosses:
            row = df[df["gloss"] == gloss]

            if row.empty:
                raise ValueError(f"Gloss not found: {gloss}")

            ordered_rows.append(row.iloc[0])

        result_df = pd.DataFrame(ordered_rows).reset_index(drop=True)

        return success_result(data=result_df)

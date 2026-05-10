import h5py
import numpy as np
import pandas as pd
from src.utils.files import dump_pkl, images_to_video
from src.utils.blender import render
from src.utils.path_manager import PathManager


DF_HEADERS = [
    "sign_id",
    "gloss",
    "fps",
    "num_frames",
    "frame_start",
    "frame_end",
]

PathManager.ensure_dirs()

def load_metadata():
    if not PathManager.METADATA_PATH.exists():
        return pd.DataFrame(columns=DF_HEADERS)

    return pd.read_csv(PathManager.METADATA_PATH)


def delete_metadata_tsl(sign_id):

    try:
        sign_id = str(sign_id)

        # Delete from metadata.csv
        if PathManager.METADATA_PATH.exists():
            df = pd.read_csv(PathManager.METADATA_PATH)

            before_count = len(df)
            df = df[df["sign_id"].astype(str) != sign_id]
            after_count = len(df)

            if before_count == after_count:
                return False

            df.to_csv(PathManager.METADATA_PATH, index=False)

        # Delete from tsl_dictionary.h5
        if PathManager.TSL_H5_PATH.exists():
            with h5py.File(PathManager.TSL_H5_PATH, "a") as h5f:

                if sign_id in h5f:
                    del h5f[sign_id]

        return True

    except Exception as e:
        print(f"[DELETE ERROR] {e}")
        return False


def get_row_by_index(index):

    df = load_metadata()

    if index is None:
        return "", ""

    if index >= len(df):
        return "", ""

    row = df.iloc[index]

    return row["sign_id"], row["gloss"]





def export_3d_json(sign_id):

    print(f"[3D] export json from sign_id: {sign_id}")

    return str(PathManager.get_3d_json_path(sign_id))


def render_keypoint(sign_id):

    print(f"[Keypoint] render from sign_id: {sign_id}")

    return str(PathManager.get_keypoint_video_path(sign_id))


def export_keypoint_json(sign_id):

    print(f"[Keypoint] export json from sign_id: {sign_id}")

    return str(PathManager.get_keypoint_json_path(sign_id))



def _create_gloss_motion(motion_id, num_frames, gender):
    try:
        with h5py.File(PathManager.TSL_H5_PATH, "r") as f:

            if motion_id not in f:
                return False, f"Motion ID '{motion_id}' not found in H5 file"

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

        return True, f"Successfully created {num_frames} motion frames for '{motion_id}'"

    except Exception as e:
        return False, f"Unexpected error: {e}"
    


import subprocess
import sys
import traceback


def render_3d_gloss(sign_id, fps, num_frames):
    try:
        print("[INFO] Creating gloss motion...")

        ok_motion, err_motion = _create_gloss_motion(
            sign_id,
            num_frames - 1,
            "neutral"
        )

        if not ok_motion:
            print(f"[ERROR] Failed to create gloss motion: {err_motion}")
            return False, err_motion

        print("[INFO] Running render subprocess...")

        # cmd = [
        #     sys.executable,
        #     "src/render_script.py",
        #     sign_id,
        #     str(fps),
        #     str(num_frames),
        # ]

        cmd = [
            sys.executable,
            "-m",
            "src.render_script",
            sign_id,
            str(fps),
            str(num_frames),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print("========== RENDER STDOUT ==========")
        print(result.stdout)

        if result.stderr:
            print("========== RENDER STDERR ==========")
            print(result.stderr)

        if result.returncode != 0:
            return False, result.stderr

        print("[INFO] Render completed")

        return True, None

    except Exception as e:
        print("\n========== ERROR ==========")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {e}")
        traceback.print_exc()
        print("========== END ERROR ==========\n")

        return False, str(e)
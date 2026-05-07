import os
import uuid
import shutil
import cv2
import subprocess
from gui.handlers.validation import validate_extract_metadata

# Config
BASE_DIR = "../upload"
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
FRAME_DIR = os.path.join(BASE_DIR, "frames")
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)


def upload(video_file):
    if video_file is None:
        return "", "", [], ""

    # -------- create id --------
    vid = str(uuid.uuid4())

    # -------- save video --------
    video_path = os.path.join(VIDEO_DIR, f"{vid}.mp4")
    shutil.copy(video_file, video_path)

    # -------- extract frames --------
    cap = cv2.VideoCapture(video_path)

    # ✅ ดึง fps จาก video
    fps = cap.get(cv2.CAP_PROP_FPS)
    # fps_str = f"{fps:.2f}"

    frame_paths = []
    frame_folder = os.path.join(FRAME_DIR, vid)
    os.makedirs(frame_folder, exist_ok=True)

    idx = 0
    while True:
        ret, frame = cap.read() 
        if not ret:
            break
        frame_path = os.path.join(frame_folder, f"{idx:04d}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_paths.append(frame_path)
        idx += 1

    cap.release()

    # ✅ return ครบทุก output
    return vid, fps, frame_paths, len(frame_paths)


def find_project_root(start_path):
    current = start_path
    while True:
        if os.path.exists(os.path.join(current, "scripts")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            raise RuntimeError("Project root not found")
        current = parent


def extract_keypoint(vid, word, fps, num_frames, frame_start, frame_end):
    return

def reconstruct_human(vid, word, fps, num_frames, frame_start, frame_end):
    if not validate_extract_metadata(vid, word, fps, num_frames, frame_start, frame_end):
        return

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = find_project_root(CURRENT_DIR)

    script_path = os.path.join(PROJECT_ROOT, "scripts", "inference_smplestx.sh")

    vid_path = os.path.join(PROJECT_ROOT, "upload", "videos", f"{vid}.mp4")

    cmd = [
        "bash",
        script_path,
        "smplest_x_h",
        vid_path,
        str(fps)
    ]

    try:
        subprocess.run(cmd, check=True)

        mesh_video_path = os.path.join(
            PROJECT_ROOT,
            "tmp",
            "mesh",
            f"result_{vid}.mp4"
        )

        if not os.path.exists(mesh_video_path):
            return None, "mesh video not found"

        return mesh_video_path, "extract success"
    
    except subprocess.CalledProcessError as e:
        print("[ERROR]", e)


import os
import glob
import pickle
import h5py
import numpy as np
import pandas as pd

from pandas.errors import EmptyDataError


def save_data(
    vid,
    gloss,
    fps,
    num_frames,
    frame_start,
    frame_end,
):

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = find_project_root(CURRENT_DIR)

    # =====================================================
    # Utility
    # =====================================================
    def load_pkl(path):
        with open(path, "rb") as f:
            return pickle.load(f)

    # =====================================================
    # Find frame pkl files
    # =====================================================
    frame_paths = sorted(
        glob.glob(
            os.path.join(
                PROJECT_ROOT,
                "tmp",
                "smplx_params",
                vid,
                "*.pkl"
            )
        )
    )

    if len(frame_paths) == 0:
        raise ValueError(
            f"No pkl files found in: {frame_paths}"
        )

    # =====================================================
    # Collect frame data
    # =====================================================
    global_orient = []
    body_pose = []
    left_hand_pose = []
    right_hand_pose = []
    jaw_pose = []
    leye_pose = []
    reye_pose = []
    transl = []

    # betas ใช้ค่าเดียวทั้งวิดีโอ
    betas = None

    for frame_path in frame_paths:

        data = load_pkl(frame_path)

        global_orient.append(data["global_orient"][0])
        body_pose.append(data["body_pose"][0])
        left_hand_pose.append(data["left_hand_pose"][0])
        right_hand_pose.append(data["right_hand_pose"][0])
        jaw_pose.append(data["jaw_pose"][0])
        leye_pose.append(data["leye_pose"][0])
        reye_pose.append(data["reye_pose"][0])
        transl.append(data["transl"][0])

        # save only first betas
        if betas is None:
            betas = data["betas"][0]

    # =====================================================
    # Convert to numpy
    # =====================================================
    global_orient = np.asarray(
        global_orient,
        dtype=np.float32
    )

    body_pose = np.asarray(
        body_pose,
        dtype=np.float32
    )

    left_hand_pose = np.asarray(
        left_hand_pose,
        dtype=np.float32
    )

    right_hand_pose = np.asarray(
        right_hand_pose,
        dtype=np.float32
    )

    jaw_pose = np.asarray(
        jaw_pose,
        dtype=np.float32
    )

    leye_pose = np.asarray(
        leye_pose,
        dtype=np.float32
    )

    reye_pose = np.asarray(
        reye_pose,
        dtype=np.float32
    )

    transl = np.asarray(
        transl,
        dtype=np.float32
    )

    betas = np.asarray(
        betas,
        dtype=np.float32
    )

    # =====================================================
    # num_frames
    # =====================================================
    num_frames = len(global_orient)

    # =====================================================
    # frame_end
    # =====================================================
    if frame_end is None:
        frame_end = num_frames - 1

    # =====================================================
    # HDF5 path
    # =====================================================
    h5_path = os.path.join(
        PROJECT_ROOT,
        "datasets",
        "tsl_dictionary.h5"
    )

    # =====================================================
    # Save to HDF5
    # =====================================================
    with h5py.File(h5_path, "a") as h5f:

        # overwrite old vid
        if vid in h5f:
            del h5f[vid]

        sample_group = h5f.create_group(vid)

        # =================================================
        # SMPLX GROUP
        # =================================================
        smplx_group = sample_group.create_group(
            "smplx"
        )

        smplx_group.create_dataset(
            "betas",
            data=betas
        )

        smplx_group.create_dataset(
            "global_orient",
            data=global_orient
        )

        smplx_group.create_dataset(
            "body_pose",
            data=body_pose
        )

        smplx_group.create_dataset(
            "left_hand_pose",
            data=left_hand_pose
        )

        smplx_group.create_dataset(
            "right_hand_pose",
            data=right_hand_pose
        )

        smplx_group.create_dataset(
            "jaw_pose",
            data=jaw_pose
        )

        smplx_group.create_dataset(
            "leye_pose",
            data=leye_pose
        )

        smplx_group.create_dataset(
            "reye_pose",
            data=reye_pose
        )

        smplx_group.create_dataset(
            "transl",
            data=transl
        )

    # =====================================================
    # Save metadata.csv
    # =====================================================
    metadata_csv_path = os.path.join(
        PROJECT_ROOT,
        "datasets",
        "metadata.csv"
    )

    row = {
        "vid": vid,
        "gloss": gloss,
        "fps": fps,
        "num_frames": num_frames,
        "frame_start": frame_start,
        "frame_end": frame_end,
    }

    try:

        if (
            os.path.exists(metadata_csv_path)
            and os.path.getsize(metadata_csv_path) > 0
        ):

            df = pd.read_csv(
                metadata_csv_path
            )

            # remove old vid
            df = df[df["vid"] != vid]

            # append new row
            df = pd.concat(
                [df, pd.DataFrame([row])],
                ignore_index=True
            )

        else:
            df = pd.DataFrame([row])

    except EmptyDataError:

        df = pd.DataFrame([row])

    # save csv
    df.to_csv(
        metadata_csv_path,
        index=False
    )

    # =====================================================
    # Done
    # =====================================================
    print("=" * 50)
    print(f"[OK] Saved video: {vid}")
    print(f"Frames: {num_frames}")
    print("=" * 50)
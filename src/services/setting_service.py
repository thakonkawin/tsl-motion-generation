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
from src.utils.transaction_manager import TransactionManager

PathManager.ensure_dirs()

def upload_sign_video(video_file):
    vid = str(uuid.uuid4())

    # create path
    frame_paths = []
    video_path = PathManager.get_upload_video_path(vid)
    frame_folder = PathManager.get_upload_frame_dir(vid)
    frame_folder.mkdir(parents=True, exist_ok=True)

    # save video
    shutil.copy(video_file, video_path)

    # extract frames
    cap = cv2.VideoCapture(video_path)

    # get frames
    fps = cap.get(cv2.CAP_PROP_FPS)

    idx = 0
    while True:
        ret, frame = cap.read() 
        if not ret:
            break
        frame_path = PathManager.get_upload_frame_path(vid, idx)
        cv2.imwrite(frame_path, frame)
        frame_paths.append(frame_path)
        idx += 1

    cap.release()

    return vid, fps, frame_paths, len(frame_paths)


def reconstruct_3d_human(video_id, frame_rate):

    script_path = PathManager.INFERENCE_SMPLESTX_SCRIPT
    vid_path = PathManager.get_upload_video_path(video_id)

    cmd = [
        "bash",
        script_path,
        "smplest_x_h",
        vid_path,
        str(frame_rate)
    ]

    try:
        subprocess.run(cmd, check=True)
        mesh_video_path = PathManager.get_tmp_mesh_video_path(video_id)

        if not os.path.exists(mesh_video_path):
            return False, None, "mesh video not found"

        return True, mesh_video_path, None
    
    except subprocess.CalledProcessError as e:
        return False, None, f"Error: {e}"
    


def _save_keypoints(paths, video_id):
    pass

    # try:
    #     # Collect parameter data
    #     global_orient = []
    #     body_pose = []
    #     left_hand_pose = []
    #     right_hand_pose = []
    #     jaw_pose = []
    #     leye_pose = []
    #     reye_pose = []
    #     transl = []
    #     betas = []

    #     for json_path in paths:
    #         data = load_pkl(pkl_path)

    #         global_orient.append(data["global_orient"][0])
    #         body_pose.append(data["body_pose"][0])
    #         left_hand_pose.append(data["left_hand_pose"][0])
    #         right_hand_pose.append(data["right_hand_pose"][0])
    #         jaw_pose.append(data["jaw_pose"][0])
    #         leye_pose.append(data["leye_pose"][0])
    #         reye_pose.append(data["reye_pose"][0])
    #         transl.append(data["transl"][0])
    #         betas.append(data["betas"][0])

        
    #     # Convert to numpy
    #     global_orient = np.asarray(global_orient, dtype=np.float32)
    #     body_pose = np.asarray(body_pose, dtype=np.float32 )
    #     left_hand_pose = np.asarray(left_hand_pose, dtype=np.float32)
    #     right_hand_pose = np.asarray(right_hand_pose, dtype=np.float32)
    #     jaw_pose = np.asarray(jaw_pose, dtype=np.float32)
    #     leye_pose = np.asarray(leye_pose, dtype=np.float32)
    #     reye_pose = np.asarray(reye_pose, dtype=np.float32)
    #     transl = np.asarray(transl, dtype=np.float32)
    #     betas = np.asarray(betas, dtype=np.float32)
            
    #     # Save to HDF5
    #     h5_path = PathManager.TSL_H5_PATH
    #     with h5py.File(h5_path, "a") as h5f:

    #         # overwrite old vid
    #         if video_id in h5f:
    #             del h5f[video_id]

    #         sample_group = h5f.create_group(video_id)

    #         # Vertice Group
    #         kp_group = sample_group.create_group("keypoints")
    #         kp_group.create_dataset("betas", data=betas)
    #         kp_group.create_dataset("global_orient", data=global_orient)
    #         kp_group.create_dataset("body_pose", data=body_pose)
    #         kp_group.create_dataset("left_hand_pose", data=left_hand_pose)
    #         kp_group.create_dataset("right_hand_pose", data=right_hand_pose)
    #         kp_group.create_dataset("jaw_pose", data=jaw_pose)
    #         kp_group.create_dataset("leye_pose", data=leye_pose)
    #         kp_group.create_dataset("reye_pose",data=reye_pose)
    #         kp_group.create_dataset("transl",data=transl)

    #     return True, None

    # except Exception:
    #     return False, "⚠️ Keypoint Error"


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
        body_pose = np.asarray(body_pose, dtype=np.float32 )
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
            vt_group.create_dataset("reye_pose",data=reye_pose)
            vt_group.create_dataset("transl",data=transl)
            vt_group.create_dataset("expression",data=expression)

        return True, None

    except Exception:
        return False, "⚠️ SMPLX Parameter Error"
    

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
        "sign_id":     video_id,
        "gloss":       gloss,
        "fps":         fps,
        "num_frames":  num_frames,
        "frame_start": frame_start,
        "frame_end":   frame_end,
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
        return True, None

    except Exception as e:
        return False, f"Unexpected error while saving metadata: {e}"
    

def _rollback_vertices(video_id):
    with h5py.File(PathManager.TSL_H5_PATH, "a") as h5f:
        if video_id in h5f:
            del h5f[video_id]


def _rollback_keypoints(video_id):
    with h5py.File(PathManager.TSL_H5_PATH, "a") as h5f:
        if video_id in h5f:
            del h5f[video_id]


def _rollback_csv(video_id):
    path = PathManager.METADATA_PATH
    if not path.exists():
        return

    df = pd.read_csv(path)
    df = df[df["sign_id"] != video_id]
    df.to_csv(path, index=False)


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
        pkl_paths = (PathManager.get_tmp_smplx_pkl_paths(video_id))
        # kp_paths = (PathManager.get_tmp_keypoint_json_paths(video_id))
        # if not pkl_paths or not kp_paths:
        #     return False, "⚠️ No dataset files"

        # # Save keypoints
        # ok_kp, err_kp = _save_keypoints(paths=kp_paths, video_id=video_id)
        # if not ok_kp:
        #     tx.rollback()
        #     return False, err_kp

        # tx.add_rollback(_rollback_keypoints, video_id)
        
        # Save vertices
        ok_vt, err_vt = _save_vertices(paths=pkl_paths, video_id=video_id)
        if not ok_vt:
            tx.rollback()
            return False, err_vt

        tx.add_rollback(_rollback_vertices, video_id)

        # Save CSV
        ok, err = _save_csv(
            path=PathManager.METADATA_PATH,
            video_id=video_id,
            gloss=gloss,
            fps=fps,
            num_frames=num_frames,
            frame_start=frame_start,
            frame_end=frame_end,
        )

        if not ok:
            tx.rollback()
            return False, err

        tx.add_rollback(_rollback_csv, video_id)

        # Success
        return True, "✅ Save dataset success"

    except Exception as e:
        tx.rollback()
        return False, str(e)
    

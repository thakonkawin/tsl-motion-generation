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


# def extract(vid, word, fps, num_frames, frame_start, frame_end):
#     if not validate_extract_metadata(vid, word, fps, num_frames, frame_start, frame_end):
#         return

#     print(f"[extract] vid={vid}, word={word}, fps={fps}, "
#           f"num_frames={num_frames}, start={frame_start}, end={frame_end}")




# def extract(vid, word, fps, num_frames, frame_start, frame_end):
#     if not validate_extract_metadata(vid, word, fps, num_frames, frame_start, frame_end):
#         return
    
#     file_path = f"upload/videos/{vid}.mp4"

#     cmd = [
#         "bash",
#         "scripts/inference_smplestx.sh",
#         "smplest_x_h",          # CKPT_NAME
#         file_path,                   # VIDEO_PATH
#         str(fps)               # FPS
#     ]

#     print(file_path)

#     try:
#         result = subprocess.run(cmd, check=True, capture_output=True, text=True)
#         print(result.stdout)
#     except subprocess.CalledProcessError as e:
#         print("[ERROR]", e.stderr)
def find_project_root(start_path):
    current = start_path
    while True:
        if os.path.exists(os.path.join(current, "scripts")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            raise RuntimeError("Project root not found")
        current = parent

def extract(vid, word, fps, num_frames, frame_start, frame_end):
    if not validate_extract_metadata(vid, word, fps, num_frames, frame_start, frame_end):
        return

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = find_project_root(CURRENT_DIR)

    script_path = os.path.join(PROJECT_ROOT, "scripts", "inference_smplestx.sh")

    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("SCRIPT:", script_path)
    print("EXISTS:", os.path.exists(script_path))

    # file_path = f"upload/videos/{vid}.mp4"

    cmd = [
        "bash",
        script_path,
        "smplest_x_h",
        vid,
        str(fps)
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("[ERROR]", e)


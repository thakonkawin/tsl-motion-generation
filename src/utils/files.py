import cv2
import pickle
import subprocess
from pathlib import Path


def load_pkl(path):
    with open(path, "rb") as f:
        return pickle.load(f)

def dump_pkl(path, data):
    with open(path, "wb") as pf:
        pickle.dump(data, pf)

def images_to_video(
    image_dir,
    output_path,
    fps=30,
):

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-start_number",
        "0",
        "-i",
        f"{image_dir}/%04d.png",

        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",

        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        output_path
    ]

    subprocess.run(cmd, check=True)
import os
import uuid
import shutil
import cv2
import gradio as gr

# Config
BASE_DIR = "./data"
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
    fps_str = f"{fps:.2f}"

    frame_paths = []
    frame_folder = os.path.join(FRAME_DIR, vid)
    os.makedirs(frame_folder, exist_ok=True)

    idx = 0
    while True:
        ret, frame = cap.read()  # ✅ แก้จาก [cap.read](http://cap.read)()
        if not ret:
            break
        frame_path = os.path.join(frame_folder, f"{idx:04d}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_paths.append(frame_path)
        idx += 1

    cap.release()

    # ✅ return ครบทุก output
    return vid, fps_str, frame_paths, str(len(frame_paths))


def extract(vid, word, fps, num_frames, frame_start, frame_end):
    print(f"[extract] vid={vid}, word={word}, fps={fps}, "
          f"num_frames={num_frames}, start={frame_start}, end={frame_end}")
    # TODO: ใส่ logic การ extract ที่นี่


def selected_frame(evt: gr.SelectData):
    """รับ index ของ frame ที่ user คลิกใน Gallery"""
    frame_index = evt.index + 1
    print(f"[selected_frame] index={frame_index}")
    return str(frame_index)


def build_setting_tab():
    with gr.Tab("Upload & Extract"):  # ✅ แก้จาก [gr.Tab](http://gr.Tab)
        with gr.Row():
            with gr.Column(scale=1):
                video_input = gr.Video(label="Upload video")  # ✅ แก้ URL format

            with gr.Column(scale=2):
                with gr.Row():
                    vid = gr.Textbox(label="video_id")
                    fps = gr.Textbox(label="fps")
                    num_frames = gr.Textbox(label="num_frames")

                gallery = gr.Gallery(  # ✅ แก้ URL format
                    label="Extracted Frames",
                    columns=8,
                    height=400,
                    interactive=True
                )

                with gr.Row():
                    selected = gr.Textbox(label="selected_frame", interactive=True)
                    gloss = gr.Textbox(label="gloss", interactive=True)
                    frame_start = gr.Textbox(label="frame_start", interactive=True)
                    frame_end = gr.Textbox(label="frame_end", interactive=True)

                extract_btn = gr.Button("Extract", variant="primary")

        # -------- Triggers --------

        # ✅ trigger upload — outputs ครบ 4 ตัว
        video_input.change(
            fn=upload,
            inputs=video_input,
            outputs=[vid, fps, gallery, num_frames],
        )

        # ✅ trigger เลือก frame จาก gallery
        gallery.select(
            fn=selected_frame,
            inputs=None,
            outputs=selected,
        )

        # ✅ แก้จาก extract_btn.click (URL format)
        extract_btn.click(
            fn=extract,
            inputs=[vid, gloss, fps, num_frames, frame_start, frame_end],
        )

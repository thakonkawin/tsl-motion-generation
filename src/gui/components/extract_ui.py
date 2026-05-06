
import gradio as gr

from gui.handlers.extract_handler import (
    upload,
    extract
)

def selected_frame(evt: gr.SelectData):
    """รับ index ของ frame ที่ user คลิกใน Gallery"""
    frame_index = evt.index + 1
    print(f"[selected_frame] index={frame_index}")
    return str(frame_index)


def build_extract_tab():
    with gr.Tab("Upload & Extract"):  # ✅ แก้จาก [gr.Tab](http://gr.Tab)
        with gr.Row():
            with gr.Column(scale=1):
                video_input = gr.Video(label="Upload video")  # ✅ แก้ URL format

            with gr.Column(scale=2):
                with gr.Row():
                    vid = gr.Textbox(label="video_id")
                    fps = gr.Number(label="fps")
                    num_frames = gr.Number(label="num_frames")

                gallery = gr.Gallery(  # ✅ แก้ URL format
                    label="Extracted Frames",
                    columns=8,
                    height=400,
                    interactive=True
                )

                with gr.Row():
                    selected = gr.Textbox(label="selected_frame", interactive=True)
                    gloss = gr.Textbox(label="gloss", interactive=True)
                    frame_start = gr.Number(label="frame_start", interactive=True)
                    frame_end = gr.Number(label="frame_end", interactive=True)

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

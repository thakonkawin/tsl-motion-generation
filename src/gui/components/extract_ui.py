
import gradio as gr

from gui.handlers.extract_handler import (
    upload,
    reconstruct_human,
    extract_keypoint,
    save_data
)

def selected_frame(evt: gr.SelectData):
    """รับ index ของ frame ที่ user คลิกใน Gallery"""
    frame_index = evt.index + 1
    print(f"[selected_frame] index={frame_index}")
    return str(frame_index)


def build_extract_tab():
    with gr.Tab("Upload & Extract"):  # ✅ แก้จาก [gr.Tab](http://gr.Tab)
        with gr.Column():
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

            extract_keypoint_btn = gr.Button("Extract Keypoints", variant="primary")
            with gr.Row():
                
                with gr.Column(scale=1):
                    viz_video = gr.Video(
                        label="Skeleton Video",
                        height=650,
                        elem_id="viz_container",
                        interactive=False,
                        autoplay=False,
                        sources=None,  # hide upload / webcam buttons
                    )
                with gr.Column(scale=2):
                    keypoint_result = gr.Textbox(label="keypoint_result", interactive=False)

                   
            reconstruct_3d_btn = gr.Button("Reconstructe 3D", variant="primary")
            with gr.Row():
                
                with gr.Column(scale=1):
                    viz_video = gr.Video(
                        label="Reconstructed Human Mesh Video",
                        height=650,
                        elem_id="viz_container",
                        interactive=False,
                        autoplay=False,
                        sources=None,  # hide upload / webcam buttons
                    )
                with gr.Column(scale=2):
                    reconstruct_result = gr.Textbox(label="reconstruct_result", interactive=False)

            save_btn = gr.Button("Save Data", variant="primary")


        video_input.change(
            fn=upload,
            inputs=video_input,
            outputs=[vid, fps, gallery, num_frames],
        )

        gallery.select(
            fn=selected_frame,
            inputs=None,
            outputs=selected,
        )

        extract_keypoint_btn.click(
            fn=extract_keypoint,
            inputs=[vid, gloss, fps, num_frames, frame_start, frame_end],
            outputs=[],
        )

        reconstruct_3d_btn.click(
            fn=reconstruct_human,
            inputs=[vid, gloss, fps, num_frames, frame_start, frame_end],
            outputs=[viz_video, reconstruct_result],
        )

        save_btn.click(
            fn=save_data,
            inputs=[vid, gloss, fps, num_frames, frame_start, frame_end],
            outputs=[],
        )
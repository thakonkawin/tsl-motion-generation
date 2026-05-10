import gradio as gr
from src.controllers.setting_controller import (
    upload_sign_video_controller,
    extract_keypoint_controller,
    reconstruct_3d_human_controller,
    save_data_controller
)

def selected_frame(evt: gr.SelectData):
    frame_index = evt.index + 1
    return str(frame_index)


def build_setting_tab():
    with gr.Tab("Settings"): 
        with gr.Column():
            with gr.Row():
                with gr.Column(scale=1):
                    video_input = gr.Video(label="Upload video")

                with gr.Column(scale=2):
                    with gr.Row():
                        vid = gr.Textbox(label="video_id")
                        fps = gr.Number(label="fps")
                        num_frames = gr.Number(label="num_frames")

                    gallery = gr.Gallery( 
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
                        sources=None,
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
                        sources=None,
                    )
                with gr.Column(scale=2):
                    reconstruct_result = gr.Textbox(label="reconstruct_result", interactive=False)

            save_btn = gr.Button("Save Data", variant="primary")


        video_input.change(
            fn=upload_sign_video_controller,
            inputs=video_input,
            outputs=[vid, fps, gallery, num_frames],
        )

        gallery.select(
            fn=selected_frame,
            inputs=None,
            outputs=selected,
        )

        extract_keypoint_btn.click(
            fn=extract_keypoint_controller,
            inputs=[vid, gloss, fps, num_frames, frame_start, frame_end],
            outputs=[],
        )

        reconstruct_3d_btn.click(
            fn=reconstruct_3d_human_controller,
            inputs=[vid, gloss, fps, num_frames, frame_start, frame_end],
            outputs=[viz_video, reconstruct_result],
        )

        save_btn.click(
            fn=save_data_controller,
            inputs=[vid, gloss, fps, num_frames, frame_start, frame_end],
            outputs=[],
        )
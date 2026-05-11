import gradio as gr
from src.const.errors import ERROR_MESSAGES, ErrorCode
from src.services.dataset_service import DatasetService
from src.services.reconstruct_service import ReconstructService


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
                        interactive=True,
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
                    keypoint_result = gr.Textbox(
                        label="keypoint_result", interactive=False
                    )

            reconstruct_mesh_btn = gr.Button("Reconstructe Mesh", variant="primary")
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
                    reconstruct_result = gr.Textbox(
                        label="reconstruct_result", interactive=False
                    )

            save_btn = gr.Button("Save Data", variant="primary")

        video_input.change(
            fn=sign_video_change,
            outputs=[
                vid,
                fps,
                gallery,
                num_frames,
                gloss,
                frame_start,
                frame_end,
                selected,
            ],
        )

        video_input.upload(
            fn=upload_sign_video_controller,
            inputs=video_input,
            outputs=[vid, fps, gallery, num_frames],
        )

        gallery.select(
            fn=selected_frame,
            inputs=None,
            outputs=selected,
        )

        reconstruct_mesh_btn.click(
            fn=reconstruct_mesh_human_controller,
            inputs=[vid, fps],
            outputs=[viz_video],
        )

        save_btn.click(
            fn=save_data_controller,
            inputs=[vid, gloss, fps, num_frames, frame_start, frame_end],
            outputs=[],
        )


def sign_video_change():
    return (
        gr.update(value=""),
        gr.update(value=None),
        gr.update(value=[]),
        gr.update(value=None),
        gr.update(value=""),
        gr.update(value=None),
        gr.update(value=None),
        gr.update(value=None),
    )


def upload_sign_video_controller(file_path):

    result = DatasetService.upload_sign_video(upload_file=file_path)

    if result.success:
        return result.data

    else:
        gr.Warning(result.message)


def reconstruct_mesh_human_controller(vid, fps):
    if vid is None or fps is None:
        gr.Warning(ERROR_MESSAGES[ErrorCode.INVALID_INPUT])
        return

    result = ReconstructService.reconstruct_mesh_human(video_id=vid, frame_rate=fps)

    if result.success:
        return result.data

    else:
        gr.Warning(result.message)


def save_data_controller(
    vid,
    gloss,
    fps,
    num_frames,
    frame_start,
    frame_end,
):

    required_fields = {
        "vid": vid,
        "gloss": gloss,
        "fps": fps,
        "num_frames": num_frames,
        "frame_start": frame_start,
        "frame_end": frame_end,
    }

    missing_fields = [key for key, value in required_fields.items() if value is None]

    if missing_fields:

        gr.Warning(f"Missing fields: " f"{', '.join(missing_fields)}")

        return

    result = DatasetService.save_to_dataset(
        video_id=vid,
        gloss=gloss,
        fps=fps,
        num_frames=num_frames,
        frame_start=frame_start,
        frame_end=frame_end,
    )

    if result.success:
        gr.Info(result.message)

    else:
        gr.Warning(f"⚠️ {result.message}")

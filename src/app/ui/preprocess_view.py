import gradio as gr

from src.controllers.preprocess_controller import PreprocessController


class PreprocessView:
    def __init__(self, controller: PreprocessController) -> None:
        self._controller = controller

    def render_preprocess_tab(self):

        with gr.Tab("Preprocessing"):
            with gr.Column():
                with gr.Row():
                    with gr.Column(scale=1):
                        video_input = gr.Video(label="Upload video")

                    with gr.Column(scale=2):
                        with gr.Row():
                            vid = gr.Textbox(label="video_id")
                            frame_rate = gr.Number(label="frame_rate")
                            num_frames = gr.Number(label="num_frames")

                        gallery = gr.Gallery(
                            label="Extracted Frames",
                            columns=8,
                            height=400,
                            interactive=True,
                            elem_id="frame_gallery",
                        )

                        with gr.Row():
                            gloss = gr.Textbox(label="gloss", interactive=True)
                            frame_start = gr.Number(
                                label="frame_start", interactive=True
                            )
                            frame_end = gr.Number(label="frame_end", interactive=True)

                # extract_keypoint_btn =
                gr.Button("Extract Keypoints", variant="primary")

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
                        # keypoint_result =
                        gr.Textbox(label="keypoint_result", interactive=False)

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
                        # reconstruct_result =
                        gr.Textbox(label="reconstruct_result", interactive=False)

                save_btn = gr.Button("Save Data", variant="primary")

            video_input.change(
                fn=self._controller.sign_video_change,
                outputs=[
                    vid,
                    frame_rate,
                    gallery,
                    num_frames,
                    gloss,
                    frame_start,
                    frame_end,
                ],
            )

            video_input.upload(
                fn=self._controller.upload_sign_video_controller,
                inputs=video_input,
                outputs=[vid, frame_rate, gallery, num_frames],
            )

            reconstruct_mesh_btn.click(
                fn=self._controller.reconstruct_mesh_human_controller,
                inputs=[vid, frame_rate],
                outputs=[viz_video],
            )

            save_btn.click(
                fn=self._controller.save_data_controller,
                inputs=[vid, gloss, frame_rate, num_frames, frame_start, frame_end],
            )

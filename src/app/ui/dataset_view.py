from typing import cast

import gradio as gr
import pandas as pd

from src.controllers.dataset_controller import DatasetController


class DatasetView:
    def __init__(self, controller: DatasetController) -> None:
        self._controller = controller

    def render_dataset_tab(self):

        df = cast(pd.DataFrame, self._controller.get_metadata_controller())

        with gr.Tab("Dataset"):
            with gr.Row():
                with gr.Column(scale=1):
                    dict_total = gr.Label(value=str(len(df)), label="Dict Total")

                    refresh_data_btn = gr.Button(
                        "Refresh",
                        variant="primary",
                    )

                    selected_sign_id = gr.Textbox(
                        label="sign_id",
                        interactive=False,
                    )

                    selected_word = gr.Textbox(label="gloss", interactive=False)

                    delete_data_btn = gr.Button(
                        "Delete",
                        variant="stop",
                    )

                with gr.Column(scale=2):
                    with gr.Tab("Mesh"):
                        video_3d = gr.Video(
                            label="Human Mesh Video",
                            height=450,
                            interactive=False,
                        )

                        with gr.Row():
                            compute_mesh_btn = gr.Button(
                                "Compute Mesh",
                                variant="primary",
                            )

                    with gr.Tab("Keypoint"):
                        video_keypoint = gr.Video(
                            label="Human Skeleton Video",
                            height=450,
                            interactive=False,
                        )

                        with gr.Row():
                            compute_keypoint_btn = gr.Button(
                                "Compute Keypoint",
                                variant="primary",
                            )

            table = gr.Dataframe(
                value=df,
                headers=df.columns.tolist(),
                label="TSL dictionary",
                interactive=True,
                show_search="search",
                show_row_numbers=True,
            )

            fps = gr.State()
            num_frames = gr.State()

            table.select(
                fn=self._controller.on_select_word,
                inputs=table,
                outputs=[
                    selected_sign_id,
                    selected_word,
                    fps,
                    num_frames,
                ],
            )

            table.change(
                fn=self._controller.refresh_data_controller,
                outputs=[dict_total, table],
            )

            refresh_data_btn.click(
                fn=self._controller.refresh_data_controller,
                outputs=[dict_total, table],
            )

            delete_data_btn.click(
                fn=self._controller.delete_data_controller, inputs=selected_sign_id
            )

            compute_mesh_btn.click(
                fn=self._controller.compute_mesh_controller,
                inputs=[selected_sign_id, fps, num_frames],
                outputs=video_3d,
            )

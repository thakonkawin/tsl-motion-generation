import gradio as gr
from src.controllers.word_controller import (
    get_metadata,
    refresh_data,
    delete_data,
    on_select_word,
    compute_3d_controller,
    download_3d_json,
    compute_keypoint,
    download_keypoint_json,
)

def build_word_tab():

    df = get_metadata()    


    with gr.Tab("Words"):

        with gr.Row():

            with gr.Column(scale=1):

                dict_total = gr.Label(
                    value=str(len(df)),
                    label="Dict Total"
                )

                refresh_data_button = gr.Button(
                    "Refresh",
                    variant="primary",
                )

                selected_sign_id = gr.Textbox(
                    label="sign_id",
                    interactive=False,
                )

                selected_word = gr.Textbox(
                    label="gloss",
                    interactive=False
                )


                delete_data_button = gr.Button(
                    "Delete",
                    variant="stop",
                )


            with gr.Column(scale=2):

                with gr.Tab("3D"):

                    video_3d = gr.Video(
                        label="Human Mesh Video",
                        height=450,
                        interactive=False,
                    )

                    with gr.Row():

                        compute_3d_button = gr.Button(
                            "Compute 3D",
                            variant="primary",
                        )

                        download_3d_button = gr.Button(
                            "Download vertices"
                        )

                with gr.Tab("Keypoint"):

                    video_keypoint = gr.Video(
                        label="Human Skeleton Video",
                        height=450,
                        interactive=False,
                    )

                    with gr.Row():

                        compute_keypoint_button = gr.Button(
                            "Compute Keypoint",
                            variant="primary",
                        )

                        download_keypoint_button = gr.Button(
                            "Download keypoints"
                        )

        table = gr.Dataframe(
            value=df,
            headers=df.columns.tolist(),
            datatype=["str"] * len(df.columns),
            label="TSL dictionary",
            interactive=True,
            show_search="search",
            show_row_numbers=True,
        )

        fps = gr.State()
        num_frames = gr.State()
        
        table.select(
            fn=on_select_word,
            inputs=table,
            outputs=[
                selected_sign_id,
                selected_word,
                fps,
                num_frames,
            ]
        )

        refresh_data_button.click(
            fn=refresh_data,
            outputs=[
                dict_total,
                table
            ],
        )

        delete_data_button.click(fn=delete_data, inputs=selected_sign_id)

        compute_3d_button.click(
            fn=compute_3d_controller,
            inputs=[selected_sign_id, fps, num_frames],
            outputs=video_3d,
        )

        download_3d_button.click(
            fn=download_3d_json,
            inputs=selected_sign_id,
        )

        compute_keypoint_button.click(
            fn=compute_keypoint,
            inputs=selected_sign_id,
            outputs=video_keypoint,
        )

        download_keypoint_button.click(
            fn=download_keypoint_json,
            inputs=selected_sign_id,
        )
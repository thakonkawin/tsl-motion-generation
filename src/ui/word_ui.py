import gradio as gr
import pandas as pd
from src.services.dataset_service import DatasetService
from src.services.render_service import RenderService


def build_word_tab():

    df = get_metadata_controller()

    with gr.Tab("Words"):

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
            ],
        )

        table.change(
            fn=refresh_data_controller,
            outputs=[dict_total, table],
        )

        refresh_data_btn.click(
            fn=refresh_data_controller,
            outputs=[dict_total, table],
        )

        delete_data_btn.click(fn=delete_data_controller, inputs=selected_sign_id)

        compute_mesh_btn.click(
            fn=compute_mesh_controller,
            inputs=[selected_sign_id, fps, num_frames],
            outputs=video_3d,
        )


def on_select_word(table_df, evt: gr.SelectData):

    if isinstance(table_df, pd.DataFrame):
        df = table_df
    else:
        df = pd.DataFrame(table_df)

    row_index = evt.index[0]

    row = df.iloc[row_index]

    return (
        str(row["sign_id"]),
        str(row["gloss"]),
        row["fps"],
        row["num_frames"],
    )


def get_metadata_controller():

    result = DatasetService.load_metadata()
    if result.success:
        return result.data
    gr.Warning(result.message)


def refresh_data_controller():

    result = DatasetService.load_metadata()
    df = result.data
    if result.success:
        return (str(len(df)), df)

    gr.Warning(result.message)


def delete_data_controller(sign_id):
    if not sign_id.strip():
        gr.Warning("Error: Sign ID not found")
        return

    result = DatasetService.delete_metadata(sign_id=sign_id)
    if not result.success:
        gr.Warning(result.message)

    gr.Info(result.message)


def compute_mesh_controller(sign_id, fps, num_frames):

    if sign_id is None or fps is None or num_frames is None:
        gr.Warning("Please select a sign before computing")

    result = RenderService.render_gloss(sign_id, fps, num_frames)
    if not result.success:
        gr.Warning(result.message)
        print(result.message)

    return result.data

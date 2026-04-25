import gradio as gr
import pandas as pd

from gui.handlers import (
    compute_3d,
    download_3d_json,
    compute_keypoint,
    download_keypoint_json
)

# dataset
df_headers = ["sign_id", "word", "fps", "num_frames"]

df_data = [
    ["sign_0001", "ฉัน", 50, 178],
    ["sign_0002", "โกรธ", 50, 230],
    ["sign_0003", "ดีใจ", 50, 134],
    ["sign_0004", "ข้าวผัด", 50, 223],
]

df = pd.DataFrame(df_data, columns=df_headers)

# select event
def on_select_word(evt: gr.SelectData):
    selected = df.iloc[evt.index[0]]
    return selected["sign_id"], selected["word"]

# 👇 function สร้าง tab (สำคัญ)
def build_word_tab():

    with gr.Tab("Words"):
        with gr.Row():
            with gr.Column():
                gr.Label(value=str(len(df)), label="Dict Total")

                selected_sign_id = gr.Textbox(label="sign_id")
                selected_word = gr.Textbox(label="word")

            with gr.Column():
                with gr.Tab("3D"):
                    video_3d = gr.Video()
                    with gr.Row():
                        compute_3d_button = gr.Button("Compute 3D", variant="primary")
                        download_3d_button = gr.Button("Download json")

                with gr.Tab("Keypoint"):
                    video_skel = gr.Video()
                    with gr.Row():
                        compute_keypoint_button = gr.Button("Compute Keypoint", variant="primary")
                        download_keypoint_button = gr.Button("Download json")

        table = gr.Dataframe(
            headers=df_headers,
            value=df,
            label="TSL dictionary",
            interactive=True,
            show_search="search",
            show_row_numbers=True,
            pinned_columns=1,
        )

        # events
        table.select(
            fn=on_select_word,
            outputs=[selected_sign_id, selected_word]
        )

        compute_3d_button.click(compute_3d, inputs=selected_sign_id)
        download_3d_button.click(download_3d_json, inputs=selected_sign_id)
        compute_keypoint_button.click(compute_keypoint, inputs=selected_sign_id)
        download_keypoint_button.click(download_keypoint_json, inputs=selected_sign_id)
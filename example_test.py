import gradio as gr

# -----------------------------
json_data = {
    "recents": [
        {
            "sentence": "eat happ angry",
            "video_path": "outputs/videos/31857233-71eb-48f7-805b-d9dbb8a87172.mp4",
        },
        {
            "sentence": "uinit ok",
            "video_path": "outputs/videos/3e76a4b1-5cb9-4d40-8d16-7b3b1a3c432c.mp4",
        },
        {
            "sentence": "poition ok",
            "video_path": "outputs/videos/d060b405-6fe0-4650-9c34-6ab29daba8ba.mp4",
        },
    ]
}

recents = json_data["recents"]


# --------------------------------
# when select example
# --------------------------------
def on_select(video_path):

    print(video_path)

    sentence = ""

    for item in recents:
        if item["video_path"] == video_path:
            sentence = item["sentence"]
            break

    return video_path, sentence


# --------------------------------
# examples
# --------------------------------
examples = [[item["video_path"]] for item in recents]


# --------------------------------
# UI
# --------------------------------
with gr.Blocks() as demo:
    gr.Markdown("## Video Gallery")

    with gr.Row():
        # ---------------- LEFT ----------------
        with gr.Column(scale=1):
            video_input = gr.Video(label="Recents", interactive=False, height=420)

            gr.Examples(
                examples=examples,
                inputs=[video_input],
                outputs=[video_input],
                fn=None,
                cache_examples=False,
                label="",
                examples_per_page=3,
            )

        # ---------------- RIGHT ----------------
        with gr.Column(scale=2):
            preview_video = gr.Video(label="Preview", height=480)

            sentence_output = gr.Textbox(label="Sentence")

            path_output = gr.Textbox(label="Video Path")

    # --------------------------------
    # event
    # --------------------------------
    video_input.change(
        fn=on_select, inputs=[video_input], outputs=[preview_video, sentence_output]
    )

    video_input.change(fn=lambda x: x, inputs=[video_input], outputs=[path_output])

demo.launch()

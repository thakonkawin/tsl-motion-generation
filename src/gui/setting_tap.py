import gradio as gr

def build_setting_tab():
    with gr.Tab("Settings"):
        with gr.Row():
            image_input = gr.Image()
            image_output = gr.Image()
        image_button = gr.Button("make word")
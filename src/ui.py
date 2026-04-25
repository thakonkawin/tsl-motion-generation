import gradio as gr
from gui.sentence_tap import build_sentence_tab
from gui.word_tap import build_word_tab
from gui.setting_tap import build_setting_tab

theme = gr.themes.Soft(primary_hue="orange")

with gr.Blocks(
    theme=theme,
    css="""
    .box {
        border: 1px;
        border-radius: 8px;
        padding: 8px;
    }

    .green-btn {
        background-color: #22c55e !important;
        color: white !important;
    }
    .green-btn:hover {
        background-color: #16a34a !important;
    }

    .red-btn {
        background-color: #ef4444 !important;
        color: white !important;
    }
    .red-btn:hover {
        background-color: #dc2626 !important;
    }

    #title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    """
) as demo:

    gr.Markdown("<div id='title'>Thai Sign Language Animation Generation</div>")

    # Tabs
    with gr.Tabs():
        build_sentence_tab()
        build_word_tab()
        build_setting_tab()

demo.launch()
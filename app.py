import gradio as gr
from src.ui.sentence_ui import build_sentence_tab
from src.ui.word_ui import build_word_tab
from src.ui.setting_ui import build_setting_tab
from src.utils.path_manager import PathManager

css = """
    #title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    """

with gr.Blocks() as demo:
    gr.Markdown("<div id='title'>Thai Sign Language Animation Generation</div>")
    
    with gr.Tabs():
        build_sentence_tab()
        build_word_tab()
        build_setting_tab()

demo.launch(
    theme=gr.themes.Soft(primary_hue="orange"),
    css=css,
    allowed_paths=[
        PathManager.UPLOAD_DIR,
        PathManager.TMP_DIR,
    ]
)
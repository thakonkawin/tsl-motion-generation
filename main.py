import gradio as gr
from gradio.themes import Soft

from src.ui.sentence_ui import build_sentence_tab
from src.ui.setting_ui import build_setting_tab
from src.ui.word_ui import build_word_tab
from src.utils.object_manager import PathManager as pm
from src.utils.path_manager import PathManager

PathManager.ensure_dirs()

pm.ensure_dirs()

css = """
    #title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    <style>
    /* overlay frame index */
    #frame_gallery .thumbnail-item {
        position: relative;
    }

    #frame_gallery .thumbnail-item::before {
        content: attr(data-testid);
        position: absolute;
        top: 4px;
        left: 4px;
        background: rgba(0,0,0,0.7);
        color: white;
        font-size: 12px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 999px;
        z-index: 100;
    }
    </style>
    """

with gr.Blocks() as demo:
    gr.Markdown("<div id='title'>Thai Sign Language Animation Generation</div>")

    with gr.Tabs():
        build_sentence_tab()
        build_word_tab()
        build_setting_tab()

demo.launch(
    theme=Soft(primary_hue="orange"),
    css=css,
    allowed_paths=[
        str(PathManager.UPLOAD_DIR),
        str(PathManager.TMP_DIR),
    ],
)

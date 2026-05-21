import gradio as gr

from src.app.ui.dataset_view import DatasetView
from src.app.ui.documents_view import DocumentView
from src.app.ui.preprocess_view import PreprocessView
from src.app.ui.text2motion_view import Text2MotionView
from src.controllers.dataset_controller import DatasetController
from src.controllers.preprocess_controller import PreprocessController
from src.controllers.text2motion_controller import Text2MotionController
from src.utils.config import AppConfig


class Application:
    def __init__(self) -> None:
        self._cfg = AppConfig()
        # controllers
        self._text2Motion_controller = Text2MotionController()
        self._dataset_controller = DatasetController()
        self._preprocess_controller = PreprocessController()

        # ui
        self._text2motion_view = Text2MotionView(
            controller=self._text2Motion_controller
        )
        self._dataset_view = DatasetView(controller=self._dataset_controller)
        self._preprocess_view = PreprocessView(controller=self._preprocess_controller)
        self._doument_view = DocumentView()

    def build(self) -> gr.Blocks:

        with gr.Blocks() as demo:
            gr.Markdown("<div id='title'>Thai Sign Language Animation Generation</div>")

            self._text2motion_view.render_text2moition_tab()
            self._dataset_view.render_dataset_tab()
            self._preprocess_view.render_preprocess_tab()
            self._doument_view.render_documents_tab()

        return demo

    def run(self) -> None:
        demo = self.build()
        demo.queue(max_size=3).launch(
            theme=gr.Theme.from_hub("Nymbo/Nymbo_Theme"),
            css_paths=self._cfg.get_path(path=self._cfg.CSS_PATH),
            allowed_paths=[
                str(self._cfg.get_path(path=self._cfg.EXAMPLE_DIR)),
                str(self._cfg.get_path(path=self._cfg.OUTPUT_DIR)),
                str(self._cfg.get_path(path=self._cfg.TMP_DIR)),
            ],
            debug=True,
        )

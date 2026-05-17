import gradio as gr
from gradio.themes import Soft

from core.controllers.gloss_controller import GlossController
from core.controllers.sentence_controller import SentenceController
from core.controllers.setting_controller import SettingController
from core.processors.human_model.smplestx_processor import SMPLestXProcessor
from core.processors.keypoint.sapiens_processor import SapiensProcessor
from core.processors.motion.motion_processor import MotionProcessor
from core.services.gloss_service import GlossService
from core.services.render.mesh_renderer import MeshRenderer
from core.services.render.skeleton_renderer import SkeletonRenderer
from core.services.sentence_service import SentenceService
from core.services.setting_service import SettingService
from core.ui.components.gloss_tab import GlossTab
from core.ui.components.sentence_tab import SentenceTab
from core.ui.components.setting_tab import SettingTab
from core.utils.config import AppConfig


class Application:
    def __init__(self) -> None:
        self.config = AppConfig()

        # Processors
        self.motion_processor = MotionGenerationProcessor(
            model_path=self.config.MOTION_MODEL_PATH,
        )

        self.human_model_processor = SMPLestXProcessor(
            checkpoint_path=self.config.HUMAN_MODEL_PATH,
        )

        self.keypoint_processor = SapiensProcessor(
            checkpoint_path=self.config.KEYPOINT_MODEL_PATH,
        )

        # Renderers
        self.mesh_renderer = MeshRenderer()
        self.skeleton_renderer = SkeletonRenderer()

        # Services
        self.gloss_service = GlossService(
            motion_processor=self.motion_processor,
            human_model_processor=self.human_model_processor,
            mesh_renderer=self.mesh_renderer,
        )

        self.sentence_service = SentenceService(
            motion_processor=self.motion_processor,
            human_model_processor=self.human_model_processor,
            mesh_renderer=self.mesh_renderer,
        )

        self.setting_service = SettingService(
            config=self.config,
        )

        # Controllers
        self.gloss_controller = GlossController(
            gloss_service=self.gloss_service,
        )

        self.sentence_controller = SentenceController(
            sentence_service=self.sentence_service,
        )

        self.setting_controller = SettingController(
            setting_service=self.setting_service,
        )

        # UI
        self.gloss_tab = GlossTab(
            controller=self.gloss_controller,
        )

        self.sentence_tab = SentenceTab(
            controller=self.sentence_controller,
        )

        self.setting_tab = SettingTab(
            controller=self.setting_controller,
        )

    def run(self) -> None:

        with gr.Blocks() as demo:
            gr.Markdown("<div id='title'>Thai Sign Language Animation Generation</div>")

            with gr.Tabs():
                self.sentence_tab.build_sentence_tab()
                # build_word_tab()
                # build_setting_tab()

        # raise NotImplementedError
        #
        demo.launch(
            theme=Soft(primary_hue="orange"),
            css_paths=self.config.CSS_PATH,
            allowed_paths=[
                # str(PathManager.UPLOAD_DIR),
                # str(PathManager.TMP_DIR),
            ],
        )

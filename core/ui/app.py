from controllers.gloss_controller import GlossController
from controllers.sentence_controller import SentenceController
from controllers.setting_controller import SettingController
from processors.human_model.smplestx_processor import SMPLestXProcessor
from processors.keypoint.sapiens_processor import SapiensProcessor
from processors.motion.motion_generation_processor import MotionGenerationProcessor
from processors.render.mesh_renderer import MeshRenderer
from processors.render.skeleton_renderer import SkeletonRenderer
from services.gloss_service import GlossService
from services.sentence_service import SentenceService
from services.setting_service import SettingService
from ui.components.gloss_tab import GlossTab
from ui.components.sentence_tab import SentenceTab
from ui.components.setting_tab import SettingTab

from utils.config import AppConfig


class Application:
    def __init__(self) -> None:
        self.config = AppConfig()

        # Processors
        self.motion_processor = MotionGenerationProcessor(
            model_path=self.config.motion_model_path,
        )

        self.human_model_processor = SMPLestXProcessor(
            model_path=self.config.human_model_path,
        )

        self.keypoint_processor = SapiensProcessor(
            checkpoint_path=self.config.keypoint_model_path,
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
        raise NotImplementedError


if __name__ == "__main__":
    app = Application()
    app.run()

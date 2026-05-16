from core.processors.interfaces.human_model_interface import HumanModelInterface
from core.processors.interfaces.motion_interface import MotionInterface
from core.processors.render.mesh_renderer import MeshRenderer
from core.utils.logger import get_logger


class SentenceService:
    def __init__(
        self,
        motion_processor: MotionInterface,
        human_model_processor: HumanModelInterface,
        mesh_renderer: MeshRenderer,
    ) -> None:
        self._motion_processor = motion_processor
        self._human_model_processor = human_model_processor
        self._mesh_renderer = mesh_renderer
        self._logger = get_logger(__name__)

    def generate_sentence_animation(self, sentence: str) -> str:
        raise NotImplementedError

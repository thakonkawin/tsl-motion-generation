from core.processors.interfaces.human_model_interface import HumanModelInterface
from core.processors.interfaces.motion_interface import MotionInterface
from core.services.render.mesh_renderer import MeshRenderer
from core.utils.logger import Logger


class GlossService:
    def __init__(
        self,
        motion_processor: MotionInterface,
        human_model_processor: HumanModelInterface,
        mesh_renderer: MeshRenderer,
    ) -> None:
        self._motion_processor = motion_processor
        self._human_model_processor = human_model_processor
        self._mesh_renderer = mesh_renderer
        self._logger = Logger()

    def generate_gloss_animation(self, gloss_sequence: list[str]) -> str:
        raise NotImplementedError

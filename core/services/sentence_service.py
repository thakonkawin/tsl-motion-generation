import time

from core.processors.interfaces.gloss_interface import GlossInterface
from core.processors.interfaces.human_model_interface import HumanModelInterface
from core.processors.interfaces.motion_interface import MotionInterface
from core.services.render.mesh_renderer import MeshRenderer
from core.utils.logger import Logger


class SentenceService:
    def __init__(
        self,
        motion_processor: MotionInterface,
        human_model_processor: HumanModelInterface,
        gloss_processor: GlossInterface,
        mesh_renderer: MeshRenderer,
    ) -> None:
        self._motion_processor = motion_processor
        self._human_model_processor = human_model_processor
        self._mesh_renderer = mesh_renderer
        self._gloss_processor = gloss_processor
        self._logger = Logger()

    def generate_sentence_animation(self, sentence: str) -> str | None:
        start = time.time()
        cleaned_text = sentence.strip()

        glosses = cleaned_text.split()

        df = self._gloss_processor.search_gloss_sequence(glosses=glosses)

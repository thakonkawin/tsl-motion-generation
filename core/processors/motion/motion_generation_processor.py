from typing import Any

from core.processors.interfaces.motion_interface import MotionInterface
from core.utils.logger import get_logger


class MotionGenerationProcessor(MotionInterface):
    def __init__(self, model_path: str) -> None:
        self._model_path = model_path
        self._logger = get_logger(__name__)

    def load_model(self) -> None:
        raise NotImplementedError

    def generate_motion(self, gloss_sequence: list[str]) -> Any:
        raise NotImplementedError

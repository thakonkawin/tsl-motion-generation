from typing import Any

from core.processors.interfaces.human_model_interface import HumanModelInterface
from core.utils.logger import get_logger


class SMPLestXProcessor(HumanModelInterface):
    def __init__(self, checkpoint_path: str) -> None:
        self._checkpoint_path = checkpoint_path
        self._logger = get_logger(__name__)

    def load_model(self) -> None:
        raise NotImplementedError

    def generate_mesh(self, motion_data: Any) -> Any:
        raise NotImplementedError

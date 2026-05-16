from abc import ABC, abstractmethod
from typing import Any


class MotionInterface(ABC):
    @abstractmethod
    def load_model(self) -> None:
        pass

    @abstractmethod
    def generate_motion(self, gloss_sequence: list[str]) -> Any:
        pass

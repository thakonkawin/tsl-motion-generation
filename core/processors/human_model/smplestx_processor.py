from abc import ABC, abstractmethod
from typing import Any


class HumanModelInterface(ABC):
    @abstractmethod
    def load_model(self) -> None:
        pass

    @abstractmethod
    def generate_mesh(self, motion_data: Any) -> Any:
        pass

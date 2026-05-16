from abc import ABC, abstractmethod
from typing import Any


class KeypointInterface(ABC):
    @abstractmethod
    def load_model(self) -> None:
        pass

    @abstractmethod
    def extract_keypoints(self, video_path: str) -> Any:
        pass

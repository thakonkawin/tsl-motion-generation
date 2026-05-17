from typing import Any

from core.processors.interfaces.keypoint_interface import KeypointInterface
from core.utils.logger import Logger


class SapiensProcessor(KeypointInterface):
    def __init__(self, checkpoint_path: str) -> None:
        self._checkpoint_path = checkpoint_path
        self._logger = Logger()

    def load_model(self) -> None:
        raise NotImplementedError

    def extract_keypoints(self, video_path: str) -> Any:
        raise NotImplementedError

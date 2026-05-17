from typing import Any

from core.utils.logger import get_logger


class MeshRenderer:
    def __init__(self) -> None:
        self._logger = get_logger(__name__)

    def render(self, mesh_data: Any, output_path: str) -> str:
        raise NotImplementedError

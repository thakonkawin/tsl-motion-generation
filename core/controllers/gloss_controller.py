from core.services.gloss_service import GlossService
from core.utils.logger import get_logger


class GlossController:
    def __init__(self, gloss_service: GlossService) -> None:
        self._gloss_service = gloss_service
        self._logger = get_logger(__name__)

    def create_gloss(self, payload: dict) -> dict:
        raise NotImplementedError

    def get_gloss(self, gloss_id: str) -> dict:
        raise NotImplementedError

    def update_gloss(self, gloss_id: str, payload: dict) -> dict:
        raise NotImplementedError

    def delete_gloss(self, gloss_id: str) -> bool:
        raise NotImplementedError

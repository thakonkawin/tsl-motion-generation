from core.services.sentence_service import SentenceService
from core.utils.logger import get_logger


class SentenceController:
    def __init__(self, sentence_service: SentenceService) -> None:
        self._sentence_service = sentence_service
        self._logger = get_logger(__name__)

    def generate_sentence(self, payload: dict) -> dict:
        raise NotImplementedError

    def get_sentence(self, sentence_id: str) -> dict:
        raise NotImplementedError

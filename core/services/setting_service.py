from core.utils.config import AppConfig
from core.utils.logger import get_logger


class SettingService:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._logger = get_logger(__name__)

    def get_settings(self) -> dict:
        raise NotImplementedError

    def update_settings(self, payload: dict) -> dict:
        raise NotImplementedError

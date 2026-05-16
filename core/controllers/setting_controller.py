from core.services.setting_service import SettingService
from core.utils.logger import get_logger


class SettingController:
    def __init__(self, setting_service: SettingService) -> None:
        self._setting_service = setting_service
        self._logger = get_logger(__name__)

    def get_settings(self) -> dict:
        raise NotImplementedError

    def update_settings(self, payload: dict) -> dict:
        raise NotImplementedError

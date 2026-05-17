from core.controllers.setting_controller import SettingController


class SettingTab:
    def __init__(self, controller: SettingController) -> None:
        self._controller = controller

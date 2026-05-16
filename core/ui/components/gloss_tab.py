from core.controllers.gloss_controller import GlossController


class GlossTab:
    def __init__(self, controller: GlossController) -> None:
        self._controller = controller

    def render(self) -> None:
        raise NotImplementedError

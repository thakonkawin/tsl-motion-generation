from core.controllers.sentence_controller import SentenceController


class SentenceTab:
    def __init__(self, controller: SentenceController) -> None:
        self._controller = controller

    def render(self) -> None:
        raise NotImplementedError

import time

from core.services.sentence_service import SentenceService
from core.utils.logger import Logger


class SentenceController:
    def __init__(self, sentence_service: SentenceService) -> None:
        self._sentence_service = sentence_service
        self._logger = Logger()

    def generate_tsl_controller(self, text_input: str) -> str | None:
        start = time.time()
        cleaned_text = text_input.strip()

        glosses = cleaned_text.split()

        # result_query = DatasetService.search_gloss_sequence(glosses=glosses)
        # if not result_query.success:
        #     raise gr.Error(result_query.message)

        # result = RenderService.render_sentence(df=result_query.data)
        # if not result.success:
        #     raise gr.Error(result.message)

        elapsed = time.time() - start
        message = f"Time Redering: {elapsed / 60:.2f} นาที"
        self._logger.success(
            message=message, module="SentenceController.generate_tsl_controller"
        )

        return result.data, cleaned_text

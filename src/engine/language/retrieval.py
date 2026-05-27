import pandas as pd

from src.utils.config import AppConfig
from src.utils.logger import Logger


class LanguageRetrieval:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def retrieve_glosses(self, text_input: str) -> pd.DataFrame:
        cleaned_text = text_input.strip()
        self._logger.info(
            message=f"cleaned_text: {cleaned_text}",
            module="LanguageRetrieval.retrieve_glosses",
        )

        glosses = cleaned_text.split()
        self._logger.info(
            message=f"glosses: {glosses}", module="LanguageRetrieval.retrieve_glosses"
        )
        filepath = self._cfg.get_path(self._cfg.METADATA_PATH)
        if not filepath.exists():
            msg = f"Path: {filepath}"
            self._logger.error(message=msg, module="LanguageRetrieval.retrieve_glosses")
            raise FileNotFoundError(msg)

        df = pd.read_csv(filepath)

        # หา gloss ที่ไม่เจอ
        missing_glosses = [
            gloss for gloss in glosses if gloss not in set(df["gloss"].astype(str))
        ]

        # ต้องเจอทุกคำ
        if missing_glosses:
            msg = f"Missing_glosses: {missing_glosses}"
            self._logger.warn(message=msg, module="LanguageRetrieval.retrieve_glosses")
            raise ValueError(msg)

        # reorder ตาม input
        ordered_rows = []

        for gloss in glosses:
            row = df[df["gloss"] == gloss]

            if row.empty:
                msg = f"Gloss not found: {gloss}"
                self._logger.error(
                    message=msg, module="GlossProcessor.search_gloss_sequence"
                )
                raise ValueError(msg)

            ordered_rows.append(row.iloc[0])

        result = pd.DataFrame(ordered_rows).reset_index(drop=True)

        self._logger.warn(
            message=str(result), module="LanguageRetrieval.retrieve_glosses"
        )
        return result

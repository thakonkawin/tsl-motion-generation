import pandas as pd

from core.processors.interfaces.gloss_interface import GlossInterface
from core.utils.config import AppConfig
from core.utils.exceptions import InvalidPathError
from core.utils.logger import Logger


class GlossProcessor(GlossInterface):
    def __init__(self, checkpoint_path: str) -> None:
        self._checkpoint_path = checkpoint_path
        self._logger = Logger()

    def search_gloss_sequence(self, glosses: list[str]) -> pd.DataFrame:
        filepath = AppConfig.ROOT_DIR / AppConfig.METADATA_PATH
        if not filepath.exists():
            msg = f"Path: {filepath}"
            self._logger.error(
                message=msg, module="GlossProcessor.search_gloss_sequence"
            )
            raise InvalidPathError(msg)

        df = pd.read_csv(filepath)

        # หา gloss ที่ไม่เจอ
        missing_glosses = [
            gloss for gloss in glosses if gloss not in set(df["gloss"].astype(str))
        ]

        # ต้องเจอทุกคำ
        if missing_glosses:
            msg = f"Missing_glosses: {missing_glosses}"
            self._logger.warn(
                message=msg, module="GlossProcessor.search_gloss_sequence"
            )
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

        return result

from abc import ABC, abstractmethod

import pandas as pd


class GlossInterface(ABC):
    @abstractmethod
    def search_gloss_sequence(self, glosses: list[str]) -> pd.DataFrame:
        pass

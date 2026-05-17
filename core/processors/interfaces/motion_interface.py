from abc import ABC, abstractmethod

import pandas as pd


class MotionInterface(ABC):
    @abstractmethod
    def _set_frame_transition(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def generate_sentence_motion(self, gloss_sequence: pd.DataFrame) -> None:
        pass

import h5py
import pandas as pd

from src.utils.config import AppConfig
from src.utils.logger import Logger


class DatasetIO:
    def __init__(self) -> None:
        self._logger = Logger()
        self._cfg = AppConfig()

    def load_metadata(self) -> pd.DataFrame:
        filepath = self._cfg.get_path(self._cfg.METADATA_PATH)
        if not filepath.exists():
            msg = f"could not resolve csv path {filepath}"
            self._logger.error(message=msg, module="DatasetIO.load_metadata")
            raise ValueError(msg)

        return pd.read_csv(filepath)

    def delete_metadata(self, sign_id: str) -> None:

        df = self.load_metadata()

        if "sign_id" not in df.columns:
            raise KeyError("Missing 'sign_id' column in metadata")

        before_count = len(df)

        filtered_df = df[df["sign_id"].astype(str) != sign_id]

        if len(filtered_df) == before_count:
            msg = f"sign_id '{sign_id}' not found in metadata"
            self._logger.error(message=msg, module="DatasetIO.delete_metadata")
            raise ValueError(msg)

        file_csv = self._cfg.get_path(self._cfg.METADATA_PATH)
        file_h5 = self._cfg.get_path(self._cfg.DATASET_PATH)

        try:
            # Save metadata
            filtered_df.to_csv(file_csv, index=False)

            # Delete HDF5 dataset
            if file_h5.exists():
                with h5py.File(file_h5, "a") as h5f:
                    if sign_id in h5f:
                        del h5f[sign_id]
                    else:
                        self._logger.warn(
                            message=f"sign_id '{sign_id}' not found in HDF5",
                            module="DatasetIO.delete_metadata",
                        )

        except Exception as e:
            self._logger.error(
                message=str(e),
                module="DatasetIO.delete_metadata",
            )
            raise FileNotFoundError(str(e))

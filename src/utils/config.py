from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(frozen=True)
    # Root
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent
    # Datasets
    METADATA_PATH: Path = Path("assets/datasets/metadata.csv")
    DATASET_PATH: Path = Path("assets/datasets/tsl_dictionary.h5")
    # Temp
    TMP_MOTION_SENTENCE_DIR: Path = Path("tmp/motions/sentences")
    TMP_MOTION_GLOSS_DIR: Path = Path("tmp/motions/gloss")
    TMP_UPLOAD_VIDEO_DIR: Path = Path("tmp/upload/videos")
    TMP_UPLOAD_FRAME_DIR: Path = Path("tmp/upload/frames")
    TMP_MESH_DIR: Path = Path("tmp/mesh")
    # Output
    OUTPUT_DIR: Path = Path("outputs")
    OUTPUT_FRAME_DIR: Path = Path("outputs/frames")
    # Blender
    BLEND_ADDON_NAME: str = "smplx_blender_addon"
    BLEND_ADDON_ZIP: Path = Path("blender/smplx_blender_addon_300_20220623.zip")
    BLEND_FILE: Path = Path("blender/tsl_4d_model.blend")
    BLEND_ADDON_DATA_DIR: Path = Path("smplx_blender_addon/data")
    # UI
    CSS_PATH: Path = Path("src/app/components/styles.css")
    # Models
    INFERENCE_SMPLESTX_SCRIPT: Path = Path("scripts/inference_smplestx.sh")

    def get_path(self, path: Path) -> Path:
        path = Path(path)
        if path.is_absolute():
            raise ValueError("path must be relative")
        return self.ROOT_DIR / path

    def get_index_file_path(
        self,
        path: str | Path,
        id: str,
        index: int,
        ext: str = "",
        mkdir: bool = False,
    ) -> Path:
        path = Path(path)
        # ext = ext.lstrip(".")

        output_path = self.ROOT_DIR / path / id / f"{index:06d}{ext}"

        if mkdir:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

from pathlib import Path
import glob


class PathManager:
    # ROOT
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent

    # DATASETS
    DATASET_DIR = ROOT_DIR / "datasets"
    METADATA_PATH = DATASET_DIR / "metadata.csv"
    TSL_H5_PATH = DATASET_DIR / "tsl_dictionary.h5"

    # UPLOAD
    UPLOAD_DIR = ROOT_DIR / "upload"
    UPLOAD_VIDEO_DIR = UPLOAD_DIR / "videos"
    UPLOAD_FRAME_DIR = UPLOAD_DIR / "frames"

    # TMP
    TMP_DIR = ROOT_DIR / "tmp"
    TMP_MESH_DIR = TMP_DIR / "mesh"
    TMP_KEYPOINT_DIR = TMP_DIR / "keypoints"
    TMP_SMPLX_DIR = TMP_DIR / "smplx_params"

    # SCRIPTS
    SCRIPT_DIR = ROOT_DIR / "scripts"
    INFERENCE_SMPLESTX_SCRIPT = SCRIPT_DIR / "inference_smplestx.sh"

    # OUTPUTS
    OUTPUT_DIR = ROOT_DIR / "outputs"
    OUTPUT_FRAME_DIR = OUTPUT_DIR / "frames"
    OUTPUT_MESH_DIR = OUTPUT_DIR / "mesh"
    OUTPUT_KEYPOINT_DIR = OUTPUT_DIR / "keypoints"
    OUTPUT_VIDEO_DIR = OUTPUT_DIR / "videos"

    # MOTIONS
    MOTION_DIR = ROOT_DIR / "motions"
    # MOTION_GLOSS_DIR = MOTION_DIR / "gloss"

    # BLENDER
    BLEND_DIR = ROOT_DIR / "blender"
    BLEND_ADDON_ZIP = BLEND_DIR / "smplx_blender_addon_300_20220623.zip"
    BLEND_FILE = BLEND_DIR / "tsl_4d_model.blend"
    BLEND_ADDON_DATA_DIR = BLEND_DIR / "smplx_blender_addon" / "data"

    # CREATE DIRECTORIES
    @classmethod
    def ensure_dirs(cls):

        dirs = [
            cls.DATASET_DIR,
            cls.UPLOAD_DIR,
            cls.UPLOAD_VIDEO_DIR,
            cls.UPLOAD_FRAME_DIR,
            cls.TMP_DIR,
            cls.TMP_MESH_DIR,
            cls.TMP_KEYPOINT_DIR,
            cls.TMP_SMPLX_DIR,
            cls.OUTPUT_DIR,
            cls.OUTPUT_FRAME_DIR,
            cls.OUTPUT_MESH_DIR,
            cls.OUTPUT_KEYPOINT_DIR,
            cls.OUTPUT_VIDEO_DIR,
            cls.MOTION_DIR,
            #
        ]

        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    # DYNAMIC PATHS
    @classmethod
    def get_upload_video_path(cls, vid):
        return cls.UPLOAD_VIDEO_DIR / f"{vid}.mp4"

    @classmethod
    def get_upload_frame_dir(cls, vid):
        return cls.UPLOAD_FRAME_DIR / vid

    @classmethod
    def get_upload_frame_path(cls, vid, idx):
        return cls.get_upload_frame_dir(vid) / f"{idx:04d}.jpg"

    @classmethod
    def get_tmp_mesh_video_path(cls, vid):
        return cls.TMP_MESH_DIR / f"result_{vid}.mp4"

    @classmethod
    def get_tmp_keypoint_dir(cls, vid):
        return cls.TMP_KEYPOINT_DIR / vid

    @classmethod
    def get_tmp_smplx_dir(cls, vid):
        return cls.TMP_SMPLX_DIR / vid

    @classmethod
    def get_tmp_smplx_pkl_paths(cls, vid):
        pattern = cls.get_tmp_smplx_dir(vid) / "*.pkl"
        return sorted(glob.glob(str(pattern)))

    @classmethod
    def get_motion_dir(cls, vid):
        return cls.MOTION_DIR / vid

    @classmethod
    def get_motion_path(cls, vid, idx):
        return cls.get_motion_dir(vid) / f"{idx:04d}.pkl"

    @classmethod
    def get_output_frame_dir(cls, vid):
        return cls.OUTPUT_FRAME_DIR / vid

    @classmethod
    def get_output_frame_path(cls, vid, idx):
        return cls.get_output_frame_dir(vid) / f"{idx:04d}.png"

    @classmethod
    def get_mesh_video_path(cls, sign_id):
        return cls.OUTPUT_MESH_DIR / f"{sign_id}.mp4"

    @classmethod
    def get_output_video_path(cls, motion_id):
        return cls.OUTPUT_VIDEO_DIR / f"{motion_id}.mp4"

    @classmethod
    def get_keypoint_video_path(cls, sign_id):
        return cls.OUTPUT_KEYPOINT_DIR / f"{sign_id}.mp4"

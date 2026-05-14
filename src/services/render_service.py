import sys
import subprocess
import pandas as pd
from src.utils.files import load_pkl
from src.utils.path_manager import PathManager
from src.utils.result import Result, error_result, success_result
from src.const.errors import ErrorCode
from src.services.motion_service import MotionService
from src.utils.path_manager import PathManager

PathManager.ensure_dirs()


class RenderService:

    def render_gloss(sign_id, fps, num_frames):
        try:
            print("[INFO] Creating gloss motion...")

            motion_result = MotionService.create_gloss_motion(
                sign_id, num_frames - 1, "neutral"
            )

            if not motion_result.success:
                return error_result(motion_result.error_code, motion_result.message)

            print("[INFO] Running render subprocess...")

            input_path = (PathManager.get_output_frame_dir(vid=sign_id),)
            output_path = (PathManager.get_mesh_video_path(sign_id=sign_id),)

            cmd = [
                sys.executable,
                "-m",
                "scripts.render_script",
                sign_id,
                str(fps),
                str(num_frames),
                input_path,
                output_path,
            ]

            subprocess.run(cmd, capture_output=True, text=True)

            print("[INFO] Render done")

            return success_result(data=str(PathManager.get_mesh_video_path(sign_id)))

        except Exception as e:
            return error_result(ErrorCode.UNKNOWN_ERROR, message=f"render_gloss: {e}")

    def render_sentence(df: pd.DataFrame):
        try:
            print("[INFO] Creating gloss motion...")

            motion_result = MotionService.create_sentence_motion(df=df)

            if not motion_result.success:
                return error_result(motion_result.error_code, motion_result.message)

            print("[INFO] Running render subprocess...")

            motion_id = motion_result.data[0]
            fps = motion_result.data[1]
            num_frames = motion_result.data[2]
            input_path = (PathManager.get_output_frame_dir(vid=motion_id),)
            output_path = (PathManager.get_output_video_path(sign_id=motion_id),)

            cmd = [
                sys.executable,
                "-m",
                "scripts.render_script",
                motion_id,
                str(fps),
                str(num_frames),
                input_path,
                output_path,
            ]

            subprocess.run(cmd, capture_output=True, text=True)

            print("[INFO] Render done")

            return success_result(
                data=str(PathManager.get_output_video_path(motion_id))
            )

        except Exception as e:
            return error_result(
                ErrorCode.UNKNOWN_ERROR, message=f"render_sentence: {e}"
            )

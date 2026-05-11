import sys
import subprocess
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

            cmd = [
                sys.executable,
                "-m",
                "scripts.render_script",
                sign_id,
                str(fps),
                str(num_frames),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return error_result(
                    error_code=ErrorCode.RENDER_FAILED, message=result.returncode
                )

            return success_result(data=str(PathManager.get_mesh_video_path(sign_id)))

        except Exception as e:
            return error_result(ErrorCode.UNKNOWN_ERROR, message=f"render_gloss: {e}")

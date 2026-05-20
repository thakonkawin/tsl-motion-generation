from src.engine.visualizations.blender import Blender
from src.utils.config import AppConfig
from src.utils.logger import Logger


class Renderer:
    def __init__(
        self, motion_id: str, motion_list: list, resolution: tuple = (512, 512)
    ) -> None:
        self._cfg = AppConfig()
        self._logger = Logger()
        self._blender = Blender()
        self.motion_id = motion_id
        self.motion_list = motion_list
        self.resolution = resolution

    def render(self):

        self._blender.install_addon()
        self._blender.set_addon()

        scene = self._blender.get_scene()
        self._blender.configure_render_quality(scene=scene, resolution=self.resolution)

        # Armature
        armature = self._blender.get_first_object(obj_type="ARMATURE")
        if armature is None:
            msg = "No ARMATURE found in scene — SMPL-X setup required."
            self._logger.error(message=msg, module="Renderer.render")
            raise RuntimeError(msg)

        self._blender.set_active(obj=armature)

        # Render Loop
        total_frames = len(self.motion_list)

        for idx, motion_path in enumerate(self.motion_list):
            self._logger.info(message=f"[Render] Loading pose {idx + 1}/{total_frames}")

            self._blender.smplx_load_pose(motion_path=str(motion_path))

            frame_path = self._cfg.get_index_file_path(
                path=self._cfg.OUTPUT_FRAME_DIR, id=self.motion_id, index=idx
            )

            # filepath ต้องไม่มี extension
            scene.render.filepath = str(frame_path.with_suffix(""))

            self._blender.render()
            self._logger.info(
                message=f"[Render] Saved frame {idx + 1}/{total_frames} → {frame_path}"
            )

        self._logger.success("[Render] Completed")

    # def render_gloss(sign_id, fps, num_frames):
    #     try:
    #         print("[INFO] Creating gloss motion...")

    #         motion_result = MotionService.create_gloss_motion(
    #             sign_id, num_frames - 1, "neutral"
    #         )

    #         if not motion_result.success:
    #             return error_result(motion_result.error_code, motion_result.message)

    #         print("[INFO] Running render subprocess...")

    #         input_dir = str(PathManager.get_output_frame_dir(vid=sign_id))
    #         output_path = str(PathManager.get_mesh_video_path(sign_id=sign_id))

    #         cmd = [
    #             sys.executable,
    #             "-m",
    #             "scripts.render_script",
    #             sign_id,
    #             str(fps),
    #             str(num_frames),
    #             input_dir,
    #             output_path,
    #         ]

    #         subprocess.run(cmd, capture_output=True, text=True)

    #         print("[INFO] Render done")

    #         return success_result(data=str(PathManager.get_mesh_video_path(sign_id)))

    #     except Exception as e:
    #         return error_result(ErrorCode.UNKNOWN_ERROR, message=f"render_gloss: {e}")

    # @staticmethod
    # def render_sentence(df: pd.DataFrame):
    #     try:
    #         print("[INFO] Creating gloss motion...")

    #         motion_result = MotionService.create_sentence_motion(df=df)

    #         if not motion_result.success:
    #             return error_result(
    #                 motion_result.error_code,
    #                 motion_result.message,
    #             )

    #         print("[INFO] Running render subprocess...")

    #         motion_id = motion_result.data[0]
    #         fps = motion_result.data[1]
    #         num_frames = motion_result.data[2]

    #         input_dir = str(PathManager.get_output_frame_dir(vid=motion_id))

    #         output_path = str(PathManager.get_output_video_path(motion_id=motion_id))

    #         cmd = [
    #             sys.executable,
    #             "-m",
    #             "scripts.render_script",
    #             motion_id,
    #             str(fps),
    #             str(num_frames),
    #             input_dir,
    #             output_path,
    #         ]

    #         subprocess.run(cmd, capture_output=True, text=True)

    #         print("[INFO] Render done")

    #         return success_result(
    #             data=str(PathManager.get_output_video_path(motion_id))
    #         )

    #     except Exception as e:
    #         return error_result(
    #             ErrorCode.UNKNOWN_ERROR,
    #             message=f"render_sentence: {e}",
    #         )

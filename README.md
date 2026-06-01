import subprocess
import sys
from pathlib import Path

import gradio as gr

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
            print(f"PROGRESS:FRAME:{idx + 1}:{total_frames}", flush=True)

            frame_path = self._cfg.get_index_file_path(
                path=self._cfg.OUTPUT_FRAME_DIR, id=self.motion_id, index=idx
            )

            scene.render.filepath = str(frame_path.with_suffix(""))

            self._blender.render()
            self._logger.info(
                message=f"[Render] Saved frame {idx + 1}/{total_frames} → {frame_path}"
            )

        self._logger.success("[Render] Completed")
ช่วยตรวจสอบหน่อยว่า ทำไม error
2026-05-31 19:03:06] [Renderer.run] [ERROR] Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 78, in execute
    obj.data.shape_keys.key_blocks["Pose%03d" % index].value = weight
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: bpy_struct: item.attr = val: ShapeKey.value expected a float type, not numpy.ndarray
Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 370, in execute
    bpy.ops.object.smplx_set_poseshapes('EXEC_DEFAULT')
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
RuntimeError: Error: Python: Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 78, in execute
    obj.data.shape_keys.key_blocks["Pose%03d" % index].value = weight
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: bpy_struct: item.attr = val: ShapeKey.value expected a float type, not numpy.ndarray
Location: /home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py:370

Traceback (most recent call last):
  File "/home/thakon/workspaces/tsl-motion-generation/src/engine/visualizations/render_script.py", line 29, in main
    renderer.render()
    ~~~~~~~~~~~~~~~^^
  File "/home/thakon/workspaces/tsl-motion-generation/src/engine/visualizations/renderer.py", line 46, in render
    self._blender.smplx_load_pose(motion_path=str(motion_path))
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/thakon/workspaces/tsl-motion-generation/src/engine/visualizations/blender.py", line 231, in smplx_load_pose
    bpy.ops.object.smplx_load_pose(filepath=motion_path)  # pyright: ignore[reportAttributeAccessIssue]
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Error: Python: Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 370, in execute
    bpy.ops.object.smplx_set_poseshapes('EXEC_DEFAULT')
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
RuntimeError: Error: Python: Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 78, in execute
    obj.data.shape_keys.key_blocks["Pose%03d" % index].value = weight
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: bpy_struct: item.attr = val: ShapeKey.value expected a float type, not numpy.ndarray
Location: /home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py:370
Location: /home/thakon/workspaces/tsl-motion-generation/src/engine/visualizations/blender.py:231


[2026-05-31 19:03:06] [Renderer.run] [ERROR] Render invalid. Subprocess failed:
Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 78, in execute
    obj.data.shape_keys.key_blocks["Pose%03d" % index].value = weight
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: bpy_struct: item.attr = val: ShapeKey.value expected a float type, not numpy.ndarray
Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 370, in execute
    bpy.ops.object.smplx_set_poseshapes('EXEC_DEFAULT')
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
RuntimeError: Error: Python: Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 78, in execute
    obj.data.shape_keys.key_blocks["Pose%03d" % index].value = weight
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: bpy_struct: item.attr = val: ShapeKey.value expected a float type, not numpy.ndarray
Location: /home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py:370

Traceback (most recent call last):
  File "/home/thakon/workspaces/tsl-motion-generation/src/engine/visualizations/render_script.py", line 29, in main
    renderer.render()
    ~~~~~~~~~~~~~~~^^
  File "/home/thakon/workspaces/tsl-motion-generation/src/engine/visualizations/renderer.py", line 46, in render
    self._blender.smplx_load_pose(motion_path=str(motion_path))
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/thakon/workspaces/tsl-motion-generation/src/engine/visualizations/blender.py", line 231, in smplx_load_pose
    bpy.ops.object.smplx_load_pose(filepath=motion_path)  # pyright: ignore[reportAttributeAccessIssue]
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: Error: Python: Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 370, in execute
    bpy.ops.object.smplx_set_poseshapes('EXEC_DEFAULT')
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
RuntimeError: Error: Python: Traceback (most recent call last):
  File "/home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py", line 78, in execute
    obj.data.shape_keys.key_blocks["Pose%03d" % index].value = weight
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: bpy_struct: item.attr = val: ShapeKey.value expected a float type, not numpy.ndarray
Location: /home/thakon/.config/blender/5.1/scripts/addons/smplx_blender_addon/operators/pose.py:370
Location: /home/thakon/workspaces/tsl-motion-generation/src/engine/visualizations/blender.py:231

แต่ถ้า รันในโปรแกรม blender load pose ไม่ error
เนื่องจากฉัน update smplx_blender_add_on

import os

import bpy

if __name__ == "__main__":
    bpy.ops.preferences.addon_install(
        filepath="assets/blender/smplx_blender_addon-1.0.3-20260511.zip", overwrite=True
    )
    bpy.ops.preferences.addon_enable(module="smplx_blender_addon")
    bpy.ops.wm.save_userpref()
    bpy.ops.wm.open_mainfile(filepath="assets/blender/tsl_model.blend")

    path = os.path.abspath("assets/blender/smplx_blender_addon/data")
    bpy.ops.file.find_missing_files(directory=path)

    bpy.data.scenes["Scene"].render.resolution_y = 512
    bpy.data.scenes["Scene"].render.resolution_x = 512
    # bpy.data.objects["Camera"].location[0] = -0.02
    bpy.data.objects["Camera"].location[1] = -0.85  # -0.725
    bpy.data.objects["Camera"].location[2] = 0.155
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.image_settings.color_mode = "RGBA"

    bpy.ops.object.smplx_load_pose(filepath="data/pose_test.pkl")
    bpy.ops.render.render()
    bpy.data.images["Render Result"].save_render("outputs/image_test_render.png")

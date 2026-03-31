import bpy
import os

# ============================================================
# CONFIG (ALL INPUTS HERE)
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    "addon": {
        "zip": os.path.join(BASE_DIR, "blender/smplx_blender_addon_300_20220623.zip"),
        "name": "smplx_blender_addon",
        "data_dir": os.path.join(BASE_DIR, "blender/smplx_blender_addon/data"),
    },
    "blend_file": os.path.join(BASE_DIR, "blender/smplx_cp.blend"),
    "pose_file": os.path.join(BASE_DIR, "POSA_rp_poses/test_image_param.pkl"),
    # "pose_file2": os.path.join(BASE_DIR, "POSA_rp_poses/rp_petra_posed_019_0_0.pkl"),
    "output_image": os.path.join(BASE_DIR, "outputs/test_img_10.png"),
    "output_dir": os.path.join(BASE_DIR, "tmp/render_frames/"),
    "render": {
        "engine": "CYCLES",
        "resolution": (512, 512),
    },
    "camera_location": (-0.05131, -1.79625, -0.000972),
}


# ============================================================
# UTILS
# ============================================================
def install_addon(cfg):
    prefs = bpy.context.preferences
    if cfg["name"] not in prefs.addons:
        print("Installing SMPL-X addon...")
        bpy.ops.preferences.addon_install(filepath=cfg["zip"])
        bpy.ops.preferences.addon_enable(module=cfg["name"])
        bpy.ops.wm.save_userpref()


def get_first_object(obj_type):
    for obj in bpy.context.scene.objects:
        if obj.type == obj_type:
            return obj
    return None


def set_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()


# ============================================================
# PIPELINE
# ============================================================

# 1) Install addon (before opening blend)
install_addon(CONFIG["addon"])

# 2) Open blend (reset state)
bpy.ops.wm.open_mainfile(filepath=CONFIG["blend_file"])

# 3) Fix missing files (addon data)
if os.path.isdir(CONFIG["addon"]["data_dir"]):
    bpy.ops.file.find_missing_files(
        directory=os.path.abspath(CONFIG["addon"]["data_dir"])
    )

# 4) Render settings (Blender 5 safe)
scene = bpy.context.scene
scene.render.engine = CONFIG["render"]["engine"]
scene.render.resolution_x, scene.render.resolution_y = CONFIG["render"]["resolution"]
scene.render.resolution_percentage = 100
scene.render.use_file_extension = True

# 5) Camera
# camera = scene.camera or get_first_object("CAMERA")
# if camera is None:
#     raise RuntimeError("No camera found in scene")

# scene.camera = camera
# camera.location = CONFIG["camera_location"]

# 6) SMPL-X armature (must be active)
armature = get_first_object("ARMATURE")
if armature is None:
    raise RuntimeError("No ARMATURE found for SMPL-X")

set_active(armature)
print("Using armature:", armature.name)


# FRAMES_PER_POSE = 10
# TOTAL_FRAMES = 60

# for frame in range(1, TOTAL_FRAMES + 1):

#     # คำนวณว่าอยู่ block ไหน
#     block_index = (frame - 1) // FRAMES_PER_POSE

#     # block คู่ = pose1, block คี่ = pose2
#     pose_path = CONFIG["pose_file"] if block_index % 2 == 0 else CONFIG["pose_file2"]

#     # load pose
#     bpy.ops.object.smplx_load_pose(filepath=pose_path)

#     # output path
#     output_path = os.path.join(CONFIG["output_dir"], f"frame_{frame:03d}.png")
#     scene.render.filepath = output_path

#     # render
#     bpy.ops.render.render(write_still=True)
#     print(f"Frame {frame:03d} -> {os.path.basename(pose_path)}")

# print("Render finished 🎬")

# # 7) Load pose + render
bpy.ops.object.smplx_load_pose(filepath=CONFIG["pose_file"])
bpy.ops.render.render()

# 8) Save render result
image = bpy.data.images.get("Render Result")
if image is None:
    raise RuntimeError("Render Result not found")

image.save_render(filepath=CONFIG["output_image"])
print("Render finished ->", CONFIG["output_image"])

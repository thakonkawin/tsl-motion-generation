import bpy
import os

# UTILS
def install_addon(zip_path, addon_name):
    prefs = bpy.context.preferences
    if addon_name not in prefs.addons:
        print("Installing SMPL-X addon...")
        bpy.ops.preferences.addon_install(filepath=zip_path)
        bpy.ops.preferences.addon_enable(module=addon_name)
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

def setup_device(device="GPU"):
    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons["cycles"].preferences

    if device == "GPU":
        # select backend ( CUDA → OPTIX → HIP → METAL)
        for compute in ["CUDA", "OPTIX", "HIP", "METAL"]:
            try:
                cycles_prefs.compute_device_type = compute
                break
            except TypeError:
                continue

        # enable all GPU
        for dev in cycles_prefs.devices:
            dev.use = True

        bpy.context.scene.cycles.device = "GPU"
        print("Using GPU rendering")

    else:
        bpy.context.scene.cycles.device = "CPU"
        print("Using CPU rendering")


# MAIN FUNCTION
def render_avatar(
    blend_file,
    pose_file,
    output_image,
    addon_zip,
    addon_name="smplx_blender_addon",
    addon_data_dir=None,
    engine="CYCLES",
    resolution=(512, 512),
    camera_location=None,
    device="GPU",
):
    """
    Render SMPL-X avatar from pose file

    Parameters:
    - blend_file: path to .blend
    - pose_file: path to .pkl pose
    - output_image: output image path
    - addon_zip: path to addon zip
    - addon_name: blender addon module name
    - addon_data_dir: path to addon data (optional)
    - engine: render engine
    - resolution: (width, height)
    - camera_location: tuple (x, y, z)
    """

    # 1) Install addon
    install_addon(addon_zip, addon_name)

    # 2) Open blend
    bpy.ops.wm.open_mainfile(filepath=blend_file)

    # 3) Fix missing files
    if addon_data_dir and os.path.isdir(addon_data_dir):
        bpy.ops.file.find_missing_files(directory=os.path.abspath(addon_data_dir))

    # 4) Render settings
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.use_file_extension = True
    
    if engine == "CYCLES":
        setup_device(device)

    # 5) Camera (optional)
    if camera_location is not None:
        cam = get_first_object("CAMERA")
        if cam:
            cam.location = camera_location

    # 6) Armature
    armature = get_first_object("ARMATURE")
    if armature is None:
        raise RuntimeError("No ARMATURE found for SMPL-X")

    set_active(armature)
    print("Using armature:", armature.name)

    # 7) Load pose + render
    # bpy.ops.object.smplx_load_pose(filepath=pose_file)
    bpy.ops.render.render()

    # 8) Save result
    image = bpy.data.images.get("Render Result")
    if image is None:
        raise RuntimeError("Render Result not found")

    os.makedirs(os.path.dirname(output_image), exist_ok=True)
    image.save_render(filepath=output_image)

    print("Render finished ->", output_image)
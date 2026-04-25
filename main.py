from src.render_avatar import render_avatar
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    render_avatar(
        blend_file=os.path.join(BASE_DIR, "blender/tsl_3d_model.blend"),
        pose_file=os.path.join(BASE_DIR, "motions/happy_tsl/frame_000047.pkl"),
        output_image=os.path.join(BASE_DIR, "outputs/test_by_code_v5.png"),
        addon_zip=os.path.join(BASE_DIR, "blender/smplx_blender_addon_300_20220623.zip"),
        addon_data_dir=os.path.join(BASE_DIR, "blender/smplx_blender_addon/data"),
        resolution=(512, 512),
        device="GPU",
    )


if __name__ == "__main__":
    main()
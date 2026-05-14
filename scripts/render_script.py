import sys
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.utils.path_manager import PathManager
from src.utils.blender import render
from src.utils.files import images_to_video


def main():
    try:
        sign_id = sys.argv[1]
        fps = int(sys.argv[2])
        num_frames = int(sys.argv[3])
        input_path = sys.argv[4]
        output_path = sys.argv[5]

        print("[SCRIPT] Preparing motion paths...")

        motion_paths = [
            PathManager.get_motion_path(sign_id, i) for i in range(num_frames - 1)
        ]

        print("[SCRIPT] Start rendering...")

        render(motion_id=sign_id, motion_lst=motion_paths)

        print("[SCRIPT] Converting images to video...")

        images_to_video(
            input_path,
            output_path,
            fps=fps,
        )

        print("[SCRIPT] Done")

    except Exception as e:
        print("\n========== SCRIPT ERROR ==========")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {e}")
        traceback.print_exc()
        print("========== END SCRIPT ERROR ==========\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

import sys
import traceback
from pathlib import Path

from src.engine.visualizations.renderer import Renderer
from src.utils.config import AppConfig


def main():
    try:
        sign_id = sys.argv[1]
        target_path = sys.argv[2]

        print("[SCRIPT] Start rendering...")
        cfg = AppConfig()

        motion_list = cfg.get_list_file_paths(
            path=Path(target_path), vid=sign_id, ext=".pkl"
        )

        renderer = Renderer(
            motion_id=sign_id,
            motion_list=motion_list,
            resolution=(512, 512),
        )
        renderer.render()

    except Exception as e:
        print("\n========== SCRIPT ERROR ==========")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {e}")
        traceback.print_exc()
        print("========== END SCRIPT ERROR ==========\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

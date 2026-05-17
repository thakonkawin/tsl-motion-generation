from core.ui.app import Application
from core.utils.path_manager import PathManager


def main():
    PathManager.ensure_dirs()

    app = Application()
    app.run()


if __name__ == "__main__":
    main()

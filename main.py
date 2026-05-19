from src.gradio_app import Application


def main():
    # PathManager.ensure_dirs()

    app = Application()
    app.run()


if __name__ == "__main__":
    main()

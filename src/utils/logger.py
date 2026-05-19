from datetime import datetime


class Logger:
    COLORS = {
        "info": "\033[96m",  # cyan
        "success": "\033[92m",  # green
        "warn": "\033[93m",  # yellow
        "error": "\033[91m",  # red
        "debug": "\033[95m",  # magenta
        "reset": "\033[0m",
    }

    @staticmethod
    def log(level="info", message="", module="APP"):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        color = Logger.COLORS.get(level, Logger.COLORS["info"])

        print(
            f"{color}[{time}] "
            f"[{module}] "
            f"[{level.upper()}] "
            f"{message}"
            f"{Logger.COLORS['reset']}"
        )

    @staticmethod
    def info(message, module="APP"):
        Logger.log("info", message, module)

    @staticmethod
    def success(message, module="APP"):
        Logger.log("success", message, module)

    @staticmethod
    def warn(message, module="APP"):
        Logger.log("warn", message, module)

    @staticmethod
    def error(message, module="APP"):
        Logger.log("error", message, module)

    @staticmethod
    def debug(message, module="APP"):
        Logger.log("debug", message, module)

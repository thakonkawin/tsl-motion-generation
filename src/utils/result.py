from typing import Any, Optional
from dataclasses import dataclass
from src.const.errors import ErrorCode, ERROR_MESSAGES


@dataclass
class Result:
    success: bool
    message: str = ""
    data: Any = None
    error_code: Optional[ErrorCode] = None


def success_result(data=None, message=""):

    return Result(success=True, data=data, message=message)


def error_result(error_code: ErrorCode, message: str = None, data=None):

    if message is None:
        message = ERROR_MESSAGES[error_code]

    return Result(success=False, error_code=error_code, message=message, data=data)

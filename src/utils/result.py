from dataclasses import dataclass
from typing import Any, Optional

from src.const.errors import ERROR_MESSAGES, ErrorCode


@dataclass
class Result:
    success: bool
    message: str = ""
    data: Any = None
    error_code: Optional[ErrorCode] = None


def success_result(data=None, message=""):

    return Result(success=True, data=data, message=message)


def error_result(
    error_code: Optional[ErrorCode] = None,
    message: str = "",
    data=None,
):
    if error_code is None:
        error_code = ErrorCode.UNKNOWN_ERROR

    if not message:
        message = ERROR_MESSAGES[error_code]

    return Result(
        success=False,
        error_code=error_code,
        message=message,
        data=data,
    )

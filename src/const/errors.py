from enum import Enum


class ErrorCode(str, Enum):

    # Common
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_INPUT = "INVALID_INPUT"

    # Metadata
    METADATA_NOT_FOUND = "METADATA_NOT_FOUND"
    INDEX_OUT_OF_RANGE = "INDEX_OUT_OF_RANGE"

    # Motion
    MOTION_NOT_FOUND = "MOTION_NOT_FOUND"
    MOTION_CREATE_FAILED = "MOTION_CREATE_FAILED"

    # Render
    RENDER_FAILED = "RENDER_FAILED"
    SUBPROCESS_ERROR = "SUBPROCESS_ERROR"

    # File
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    H5_READ_ERROR = "H5_READ_ERROR"

    # Reconstruct
    RECONSTRUCT_FAILED = "RECONSTRUCT_FAILED"


ERROR_MESSAGES = {
    ErrorCode.UNKNOWN_ERROR: "Unknown error occurred",
    ErrorCode.INVALID_INPUT: "Invalid input",
    ErrorCode.METADATA_NOT_FOUND: "Metadata file not found",
    ErrorCode.INDEX_OUT_OF_RANGE: "Index out of range",
    ErrorCode.MOTION_NOT_FOUND: "Motion ID not found",
    ErrorCode.MOTION_CREATE_FAILED: "Failed to create motion",
    ErrorCode.RENDER_FAILED: "Render process failed",
    ErrorCode.SUBPROCESS_ERROR: "Subprocess execution failed",
    ErrorCode.FILE_NOT_FOUND: "File not found",
    ErrorCode.H5_READ_ERROR: "Unable to read H5 file",
    #
    ErrorCode.RECONSTRUCT_FAILED: "Model for reconstruct human failed",
}

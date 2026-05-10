import gradio as gr

# Notification helpers
def notify_warning(message: str) -> None:
    gr.Warning(message)


def notify_success(message: str) -> None:
    gr.Info(message)


def notify_error(message: str) -> None:
    gr.Error(message)


# Field-level validators (return bool)
def validate_sign(sign_id) -> bool:
    if not sign_id:
        notify_warning("Please select a sign before computing.")
        return False
    return True


def validate_gloss(gloss: str) -> bool:
    if not gloss or not gloss.strip():
        notify_warning("Please enter a gloss sequence (e.g., ข้าวผัด ฉัน กิน).")
        return False
    return True


def validate_3d_vertices(frame_paths: list) -> bool:
    if not frame_paths:
        notify_warning("Please reconstruct 3D first.")
        return False
    return True



# Form-level validator
def validate_extract_metadata(
    vid,
    word: str,
    fps: float,
    num_frames: int,
    frame_start: int,
    frame_end: int,
) -> bool:
    
    checks: list[tuple[bool, str]] = [
        (vid is not None,                                   "Please upload a video."),
        (bool(word and word.strip()),                       "Please enter a gloss."),
        (fps is not None and fps > 0,                       "FPS must be greater than 0."),
        (num_frames is not None and num_frames > 0,         "Invalid number of frames."),
        (1 <= frame_start < num_frames,                     "frame_start is out of range."),
        (
            frame_end == -1 or (frame_start < frame_end <= num_frames),
            "frame_end is invalid (must be -1 or in range frame_start < frame_end ≤ num_frames).",
        ),
    ]

    for condition, message in checks:
        if not condition:
            notify_warning(message)
            return False

    return True
import gradio as gr

def validate_sign(sign_id):
    if not sign_id:
        gr.Warning("⚠️ Please select a sign before computing")
        return False
    return True        


def validate_extract_metadata(vid, word, fps, num_frames, frame_start, frame_end):
    # check required fields
    if vid is None:
        gr.Warning("⚠️ Please upload a video")
        return False

    if not word:
        gr.Warning("⚠️ Please enter a gloss")
        return False

    if fps is None or fps <= 0:
        gr.Warning("⚠️ FPS must be greater than 0")
        return False

    if num_frames is None or num_frames <= 0:
        gr.Warning("⚠️ Invalid number of frames")
        return False

    # check frame range
    if frame_start <= 0 or frame_start >= num_frames:
        gr.Warning("⚠️ frame_start is out of range")
        return False

    if frame_end != -1 and (frame_end <= frame_start or frame_end > num_frames):
        gr.Warning("⚠️ frame_end is invalid")
        return False

    return True


def validate_gloss(gloss):
    if not gloss or not gloss.strip():
        gr.Warning("⚠️ Please enter a gloss sequence (e.g., ข้าวผัด ฉัน กิน)")
        return False
    return True
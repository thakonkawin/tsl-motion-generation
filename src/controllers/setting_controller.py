from src.controllers.validators import (
    notify_warning, 
    notify_success,
    validate_extract_metadata, 
)
from src.services.setting_service import (
    upload_sign_video,
    reconstruct_3d_human,
    save_to_dataset
)


def upload_sign_video_controller(file_upload):
    if file_upload is None:
        notify_warning("⚠️ Fe ilupload invalid")

    vid, fps, gallery, num_frames = upload_sign_video(video_file=file_upload)
    return vid, fps, gallery, num_frames

def extract_keypoint_controller(vid, word, fps, num_frames, frame_start, frame_end):
    return

def reconstruct_3d_human_controller(vid, word, fps, num_frames, frame_start, frame_end):
    if not validate_extract_metadata(vid, word, fps, num_frames, frame_start, frame_end):
        return

    ok, path, err = reconstruct_3d_human(video_id=vid, frame_rate=fps)
    if not ok:
        notify_warning(f"⚠️ {err}")
    return path, "success"

def save_data_controller(
    vid,
    gloss,
    fps,
    num_frames,
    frame_start,
    frame_end,
):
    
    print(num_frames)

    ok, msg = save_to_dataset(
        video_id=vid,
        gloss=gloss,
        fps=fps,
        num_frames=num_frames,
        frame_start=frame_start,
        frame_end=frame_end,
    )

    if not ok:
        notify_warning(f"⚠️ {msg}")
        
    notify_success(msg)
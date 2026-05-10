import gradio as gr
import pandas as pd
from src.utils.path_manager import PathManager
from src.controllers.validators import (
    validate_sign, 
    notify_success, 
    notify_warning,
)
from src.services.word_service import (
    load_metadata,
    delete_metadata_tsl,
    render_3d_gloss,
    export_3d_json,
    render_keypoint,
    export_keypoint_json,
)


def get_metadata():
    return load_metadata()


def refresh_data():

    df = load_metadata()

    return (
        str(len(df)),
        df
    )

def delete_data(sign_id):
    if not sign_id.strip():
        notify_warning("Error: Sign ID not found")
        return None
    if not delete_metadata_tsl(sign_id):
        notify_warning("Error: can not deleted datasets")
    notify_success("✅ Delete data success")



def on_select_word(table_df, evt: gr.SelectData):

    if isinstance(table_df, pd.DataFrame):
        df = table_df
    else:
        df = pd.DataFrame(table_df)

    row_index = evt.index[0]

    row = df.iloc[row_index]

    return (
        str(row["sign_id"]),
        str(row["gloss"]),
        row["fps"],
        row["num_frames"],
    )


def compute_3d_controller(sign_id, fps, num_frames):
    if not validate_sign(sign_id):
        return None

    ok, err = render_3d_gloss(sign_id, fps, num_frames)
    if not ok:
        notify_warning(err)

    return str(PathManager.get_3d_video_path(sign_id))


def download_3d_json(sign_id):

    if not validate_sign(sign_id):
        return None

    return export_3d_json(sign_id)


def compute_keypoint(sign_id):

    if not validate_sign(sign_id):
        return None

    return render_keypoint(sign_id)


def download_keypoint_json(sign_id):

    if not validate_sign(sign_id):
        return None

    return export_keypoint_json(sign_id)
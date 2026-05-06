from gui.handlers.validation import validate_sign

def compute_3d(sign_id):
    if not validate_sign(sign_id):
        return
    print(f"[3D] render from sign_id: {sign_id}")

def download_3d_json(sign_id):
    if not validate_sign(sign_id):
        return
    print(f"[3D] export json from sign_id: {sign_id}")

def compute_keypoint(sign_id):
    if not validate_sign(sign_id):
        return
    print(f"[Keypoint] render from sign_id: {sign_id}")

def download_keypoint_json(sign_id):
    if not validate_sign(sign_id):
        return
    print(f"[Keypoint] export json from sign_id: {sign_id}")



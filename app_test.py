#============================================================
# Standard library
# ============================================================
import atexit
import base64
import importlib
import json
import logging
import os
import pickle
import shutil
import site
import sys
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Union

# ============================================================
# Third-party
# ============================================================
import cv2
import decord
from decord import cpu
from einops import rearrange
import gradio as gr
import imageio
import numpy as np
from scipy.signal import savgol_filter
from scipy.spatial.transform import Rotation as R
import torch

try:
    import spaces
except ImportError:
    class spaces:
        @staticmethod
        def GPU(func):
            return func

from huggingface_hub import hf_hub_download
from pytorch3d.renderer import PointLights

# ============================================================
# Local / project
# ============================================================
from models.modules.ehm import EHM_v2
from models.modules.renderer.body_renderer import Renderer2 as BodyRenderer
from models.pipeline.ehm_pipeline import Ehm_Pipeline
from utils.general_utils import ConfigDict, add_extra_cfgs, device_parser, rtqdm
from utils.graphics_utils import GS_Camera
from utils.pipeline_utils import to_tensor

# ============================================================
# Package migration (pytorch3d / chumpy)
# ============================================================
def migrate_precompiled_packages():
    target_sp = site.getsitepackages()[0]
    packages = {
        "pytorch3d": ["pytorch3d", "pytorch3d-0.7.8.dist-info"],
        "chumpy":    ["chumpy",    "chumpy-0.70.dist-info"],
    }
    print(f"📦 Migration check in: {os.getcwd()}")
    for pkg_name, folders in packages.items():
        try:
            importlib.import_module(pkg_name)
            print(f"✅ {pkg_name} already available, skipping.")
            continue
        except ImportError:
            print(f"🔍 {pkg_name} not found, migrating...")
        for folder in folders:
            src = os.path.abspath(folder)
            dst = os.path.join(target_sp, folder)
            if not os.path.exists(src):
                print(f"❓ Source missing: {folder}")
                continue
            try:
                if os.path.exists(dst):
                    shutil.rmtree(dst) if os.path.isdir(dst) else os.remove(dst)
                shutil.copytree(src, dst)
                print(f"🚚 Migrated: {folder}")
            except Exception as e:
                print(f"❌ Failed to migrate {folder}: {e}")

    importlib.invalidate_caches()
    if target_sp not in sys.path:
        sys.path.insert(0, target_sp)

    try:
        import torch
        torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
        os.environ["LD_LIBRARY_PATH"] = torch_lib + ":" + os.environ.get("LD_LIBRARY_PATH", "")
        print("🔗 LD_LIBRARY_PATH updated.")
    except Exception as e:
        print(f"⚠️ Could not set LD_LIBRARY_PATH: {e}")

# migrate_precompiled_packages()

try:
    import chumpy
    import pytorch3d
    from pytorch3d import _C
    print(f"🎉 All systems go! PyTorch3D GPU: {hasattr(_C, 'rasterize_meshes')}")
except Exception as e:
    print(f"🚨 Validation failed: {e}")

# ============================================================
# Runtime config
# ============================================================
os.environ["LD_LIBRARY_PATH"] = (
    f"{os.environ['CONDA_PREFIX']}/lib:" + os.environ.get("LD_LIBRARY_PATH", "")
)

logger = logging.getLogger(__name__)
TORCH_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

meta_cfg = add_extra_cfgs(ConfigDict(model_config_path=os.path.join("configs", "infer.yaml")))

body_renderer = BodyRenderer("assets/SMPLX", 1024, focal_length=24.0)

ehm_basemodel = hf_hub_download(repo_id="BestWJH/PEAR_models", filename="ehm_model_stage1.pt", repo_type="model")
ehm_model = Ehm_Pipeline(meta_cfg)
_state = torch.load(ehm_basemodel, map_location="cpu", weights_only=True)
ehm_model.backbone.load_state_dict(_state["backbone"], strict=False)
ehm_model.head.load_state_dict(_state["head"], strict=False)

ehm = EHM_v2("assets/FLAME", "assets/SMPLX")

thread_pool_executor = ThreadPoolExecutor(max_workers=2)

# ============================================================
# Helpers
# ============================================================
def get_lights(device):
    return PointLights(device=device, location=[[0.0, -1.0, -10.0]])


def build_cameras_kwargs(batch_size, focal_length):
    screen_size = (
        torch.tensor([1024, 1024], device=TORCH_DEVICE).float()[None].repeat(batch_size, 1)
    )
    return {
        "principal_point": torch.zeros(batch_size, 2, device=TORCH_DEVICE).float(),
        "focal_length": focal_length,
        "image_size": screen_size,
        "device": TORCH_DEVICE,
    }


def pad_and_resize(img, target_size=512):
    h, w = img.shape[:2]
    scale = min(target_size / h, target_size / w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    out = np.zeros((target_size, target_size, 3), dtype=np.uint8)
    x_off, y_off = (target_size - new_w) // 2, (target_size - new_h) // 2
    out[y_off:y_off + new_h, x_off:x_off + new_w] = resized
    return out


def delete_later(path: Union[str, os.PathLike], delay: int = 600):
    def _delete():
        try:
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        except Exception as e:
            logger.warning(f"Failed to delete {path}: {e}")

    thread_pool_executor.submit(lambda: (time.sleep(delay), _delete()))
    atexit.register(_delete)


def create_user_temp_dir():
    session_id = str(uuid.uuid4())[:8]
    temp_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "temp_local", f"session_{session_id}"
    )
    os.makedirs(temp_dir, exist_ok=True)
    delete_later(temp_dir, delay=600)
    return temp_dir


def get_video_name(path):
    return os.path.splitext(os.path.basename(path))[0]


def extract_first_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if ret else None


def numpy_to_base64(arr):
    return base64.b64encode(arr.tobytes()).decode("utf-8")


def polynomial_smooth(sequence, window_size=5, polyorder=2):
    seq = np.asarray(sequence.cpu())
    assert seq.ndim >= 2, f"Input must be at least 2D, got shape={seq.shape}"
    assert window_size % 2 == 1, "window_size must be odd"
    assert polyorder < window_size, "polyorder must be < window_size"
    return savgol_filter(seq, window_length=window_size, polyorder=polyorder, axis=0, mode="interp")


def orthonorm_batch(rotmats):
    out = []
    for Rm in rotmats:
        U, _, Vt = np.linalg.svd(Rm)
        out.append(U @ Vt)
    return np.stack(out)


def rotmat_to_aa_safe(tensor):
    """
    input: (3,3) หรือ (J,3,3)
    output: (1, J*3)
    """
    arr = tensor.detach().cpu().numpy()

    if arr.ndim == 2:
        arr = arr.reshape(1, 3, 3)

    arr = arr.reshape(-1, 3, 3)
    arr = orthonorm_batch(arr)

    aa = R.from_matrix(arr).as_rotvec()  # (J,3)
    aa_flat = aa.reshape(1, -1)          # (1, J*3)

    return torch.tensor(aa_flat, dtype=torch.float32).to(TORCH_DEVICE)


def rotmat_to_aa_ehm(tensor):
    """
    input: (J,3,3)
    output: (1, J, 3)
    """
    arr = tensor.detach().cpu().numpy().reshape(-1, 3, 3)
    arr = orthonorm_batch(arr)

    aa = R.from_matrix(arr).as_rotvec()  # (J,3)

    return torch.tensor(aa[None], dtype=torch.float32).to(TORCH_DEVICE)


def rotmat_to_aa_flat(tensor):
    """
    input: (J,3,3)
    output: (1, J*3)
    """
    arr = tensor.detach().cpu().numpy().reshape(-1, 3, 3)
    arr = orthonorm_batch(arr)

    aa = R.from_matrix(arr).as_rotvec()  # (J,3)

    return torch.tensor(aa.reshape(1, -1), dtype=torch.float32).to(TORCH_DEVICE)

# ============================================================
# Video upload
# ============================================================
def handle_video_upload(video):
    if video is None:
        return None

    user_temp_dir = create_user_temp_dir()
    input_source = video if isinstance(video, str) else video.name
    video_name = get_video_name(input_source)
    video_path = os.path.join(user_temp_dir, f"{video_name}.mp4")

    try:
        reader = imageio.get_reader(input_source)
        fps = reader.get_meta_data().get("fps", 30)
        writer = imageio.get_writer(video_path, fps=fps, codec="libx264", quality=8)
        for frame in reader:
            writer.append_data(frame)
        reader.close()
        writer.close()
    except Exception as e:
        print(f"imageio error: {e}")
        fps = 30

    print(f"📁 Video saved to: {video_path}")

    frame = extract_first_frame(video_path)
    if frame is None:
        return None

    h, w = frame.shape[:2]
    scale = 336 / min(h, w)
    new_h, new_w = int(h * scale) // 2 * 2, int(w * scale) // 2 * 2
    frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    return json.dumps({
        "data": numpy_to_base64(frame),
        "shape": frame.shape,
        "dtype": str(frame.dtype),
        "temp_dir": user_temp_dir,
        "video_name": video_name,
        "video_path": video_path,
        "fps": fps,
    })


# ============================================================
# Inference
# ============================================================
@torch.no_grad()
def mesh_inference(temp_dir, video_name, fps):

    global body_renderer, ehm_model, ehm
    body_renderer = body_renderer.to(TORCH_DEVICE)
    ehm_model = ehm_model.to(TORCH_DEVICE)
    ehm = ehm.to(TORCH_DEVICE)

    video_path = os.path.join(temp_dir, f"{video_name}.mp4")
    out_dir = os.path.join(temp_dir, "results")
    smplx_param_dir = os.path.join(out_dir, "smplx_params")
    os.makedirs(smplx_param_dir, exist_ok=True)

    video_reader = decord.VideoReader(video_path, ctx=cpu(0))

    # =========================
    # Forward
    # =========================
    body_seq, flame_seq, cam_seq = [], [], []

    for i in range(len(video_reader)):
        frame = video_reader[i].asnumpy()
        img = pad_and_resize(frame, 256)
        img = torch.permute(to_tensor(img, TORCH_DEVICE)/255, (2,0,1)).unsqueeze(0)

        out = ehm_model(img)
        body_seq.append(out["body_param"])
        flame_seq.append(out["flame_param"])
        cam_seq.append(out["pd_cam"])

    # =========================
    # Smooth
    # =========================
    def smooth_cat(seq, keys, win, poly):
        result = {}
        for k in keys:
            t = torch.cat([s[k] for s in seq], dim=0)
            if t.ndim == 4 and t.shape[1] == 1:
                t = t.squeeze(1)
            result[k] = torch.tensor(polynomial_smooth(t, win, poly)).to(TORCH_DEVICE)
        return result

    body_keys = ["global_pose","body_pose","left_hand_pose","right_hand_pose",
                 "hand_scale","head_scale","exp","shape"]

    flame_keys = ["eye_pose_params","pose_params","jaw_params",
                  "eyelid_params","expression_params","shape_params"]

    p1 = smooth_cat(body_seq, body_keys, 7, 2)
    p2 = smooth_cat(flame_seq, flame_keys, 5, 2)

    cams = torch.tensor(polynomial_smooth(torch.cat(cam_seq, dim=0), 7, 2)).to(TORCH_DEVICE)

    all_meshes_img = []

    # =========================
    # Main loop
    # =========================
    for idx in range(p1["global_pose"].shape[0]):

        # -------- body dict --------
        body_dict = {
            "global_pose":     rotmat_to_aa_ehm(p1["global_pose"][idx]),
            "body_pose":       rotmat_to_aa_ehm(p1["body_pose"][idx]),
            "left_hand_pose":  rotmat_to_aa_ehm(p1["left_hand_pose"][idx]),
            "right_hand_pose": rotmat_to_aa_ehm(p1["right_hand_pose"][idx]),

            "hand_scale": p1["hand_scale"][idx:idx+1],
            "head_scale": p1["head_scale"][idx:idx+1],
            "exp": p1["exp"][idx:idx+1],
            "shape": p1["shape"][idx:idx+1],

            "eye_pose": None,
            "jaw_pose": None,
            "joints_offset": None,
        }

        flame_dict = {k: p2[k][idx:idx+1] for k in flame_keys}

        # -------- render --------
        pd_smplx = ehm(body_dict, flame_dict, pose_type="aa")

        cam = cams[idx:idx+1]
        camera = GS_Camera(
            **build_cameras_kwargs(1, 24),
            R=cam[:, :3, :3],
            T=cam[:, :3, 3]
        )

        img = body_renderer.render_mesh(
            pd_smplx["vertices"][None,0],
            camera,
            lights=get_lights(TORCH_DEVICE)
        )

        img = img[:, :3].cpu().numpy().clip(0,255).astype(np.uint8)[0].transpose(1,2,0)
        all_meshes_img.append(img)

        # =========================
        # PKL
        # =========================
        eye = p2["eye_pose_params"][idx].cpu().numpy()
        transl = cams[idx][:3,3].cpu().numpy().reshape(1,3)

        frame_data = {
            "global_orient": rotmat_to_aa_flat(p1["global_pose"][idx]).cpu().numpy().astype(np.float32),
            "body_pose": rotmat_to_aa_flat(p1["body_pose"][idx]).cpu().numpy().astype(np.float32),
            "left_hand_pose": rotmat_to_aa_flat(p1["left_hand_pose"][idx]).cpu().numpy().astype(np.float32),
            "right_hand_pose": rotmat_to_aa_flat(p1["right_hand_pose"][idx]).cpu().numpy().astype(np.float32),

            "betas": p1["shape"][idx].cpu().numpy()[:10].reshape(1,-1).astype(np.float32),

            "expression": p2["expression_params"][idx].cpu().numpy()[:10].reshape(1,-1).astype(np.float32),
            "jaw_pose": p2["jaw_params"][idx].cpu().numpy().reshape(1,3).astype(np.float32),

            "leye_pose": eye[:3].reshape(1,3).astype(np.float32),
            "reye_pose": eye[3:6].reshape(1,3).astype(np.float32),

            "transl": transl.astype(np.float32),
            "gender": "neutral",
        }

        # -------- DEBUG --------
        if idx == 0:
            print("\n====== PKL CHECK ======")

            render_pose = body_dict["body_pose"].cpu().numpy().reshape(1,-1)
            pkl_pose = frame_data["body_pose"]

            print("pose diff:", np.abs(render_pose - pkl_pose).mean())

            test_body = {
                "global_pose": torch.tensor(frame_data["global_orient"]).reshape(1,1,3).to(TORCH_DEVICE),
                "body_pose": torch.tensor(frame_data["body_pose"]).reshape(1,21,3).to(TORCH_DEVICE),
                "left_hand_pose": torch.tensor(frame_data["left_hand_pose"]).reshape(1,15,3).to(TORCH_DEVICE),
                "right_hand_pose": torch.tensor(frame_data["right_hand_pose"]).reshape(1,15,3).to(TORCH_DEVICE),

                "hand_scale": p1["hand_scale"][idx:idx+1],
                "head_scale": p1["head_scale"][idx:idx+1],
                "exp": p1["exp"][idx:idx+1],
                "shape": p1["shape"][idx:idx+1],

                "eye_pose": None,
                "jaw_pose": None,
                "joints_offset": None,
            }

            test_out = ehm(test_body, flame_dict, pose_type="aa")

            v_diff = torch.abs(test_out["vertices"] - pd_smplx["vertices"]).mean()
            print("vertex diff:", v_diff.item())

        # -------- SAVE --------
        with open(os.path.join(smplx_param_dir, f"frame_{idx:04d}.pkl"), "wb") as f:
            pickle.dump(frame_data, f)

    # =========================
    # Final
    # =========================
    if not all_meshes_img:
        raise RuntimeError("No frames generated.")

    mesh_video_path = os.path.join(out_dir, "mesh_video.mp4")
    imageio.mimwrite(mesh_video_path, all_meshes_img, fps=fps)

    print("✅ EHM processing completed.")


# ============================================================
# Gradio callback
# ============================================================
def launch_viz(original_image_state):
    if original_image_state is None:
        return None, None
    try:
        data = json.loads(original_image_state)
        temp_dir   = data.get("temp_dir", "temp_local")
        video_name = data.get("video_name", "video")
        fps        = data.get("fps", 30)

        print(f"🚀 Tracking: {video_name}")
        out_dir = os.path.join(temp_dir, "results")
        os.makedirs(out_dir, exist_ok=True)

        mesh_inference(temp_dir, video_name, fps)
        delete_later(temp_dir, delay=600)

        mesh_video = os.path.join(out_dir, "mesh_video.mp4")
        npz_path   = os.path.join(out_dir, "results.npz")

        if os.path.exists(mesh_video):
            print("✅ Tracking completed!")
            return mesh_video, (npz_path if os.path.exists(npz_path) else None)
        print("❌ No results generated.")
        return None, None
    except Exception as e:
        print(f"❌ Error in launch_viz: {e}")
        traceback.print_exc()
        return None, None


# ============================================================
# Gradio UI
# ============================================================
CSS = """
.gradio-container { max-width: 1200px !important; margin: auto !important; }
.gr-form { background: transparent !important; border: none !important;
           box-shadow: none !important; padding: 0 !important; }
#viz_container {
    height: 650px !important; min-height: 650px !important; max-height: 650px !important;
    width: 100% !important; padding: 12px !important; overflow: hidden !important;
    box-sizing: border-box !important; border-radius: 14px !important;
    border: 1px solid rgba(148,163,184,0.6) !important; background: #fff !important;
    box-shadow: 0 10px 24px rgba(15,23,42,0.12) !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
#video_input { height: 300px !important; min-height: 300px !important; max-height: 300px !important; }
#video_input video { height: 260px !important; max-height: 260px !important;
                     object-fit: contain !important; background: #f8f9fa; }
.horizontal-examples, .horizontal-examples > *, .horizontal-examples * {
    background: transparent !important; background-color: transparent !important; border: none !important;
}
.horizontal-examples [data-testid="examples"] > div {
    overflow-x: auto !important; overflow-y: hidden !important;
    scrollbar-width: thin; scrollbar-color: #667eea transparent; margin-top: 10px;
}
.horizontal-examples [data-testid="examples"] table {
    display: flex !important; flex-wrap: nowrap !important;
    min-width: max-content !important; gap: 15px !important; padding: 10px 0;
}
.horizontal-examples [data-testid="examples"] tbody {
    display: flex !important; flex-direction: row !important; gap: 15px !important;
}
.horizontal-examples [data-testid="examples"] tr {
    display: flex !important; flex-direction: column !important;
    min-width: 160px !important; max-width: 160px !important;
    background: white !important; border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.12); cursor: pointer; overflow: hidden;
    transition: all 0.3s ease;
}
.horizontal-examples [data-testid="examples"] tr:hover {
    transform: translateY(-4px); box-shadow: 0 8px 20px rgba(102,126,234,0.25);
}
.horizontal-examples [data-testid="examples"] td { text-align: center !important;
    padding: 0 !important; border: none !important; background: transparent !important; }
.horizontal-examples [data-testid="examples"] video {
    border-radius: 8px 8px 0 0 !important; width: 100% !important;
    height: 90px !important; object-fit: cover !important; background: #f8f9fa !important;
}
.horizontal-examples [data-testid="examples"] td:last-child {
    font-size: 11px !important; font-weight: 600 !important; color: #333 !important;
    padding: 8px 12px !important;
    background: linear-gradient(135deg, #f8f9ff 0%, #e6f3ff 100%) !important;
    border-radius: 0 0 8px 8px;
}
"""

print("🎨 Creating Gradio interface...")

with gr.Blocks(theme=gr.themes.Soft(), title="🎯 PEAR", css=CSS) as demo:

    gr.Markdown("""
    # ✨ PEAR
    Welcome to [PEAR](https://wujh2001.github.io/PEAR/)!
    Reconstruct human mesh from a single video.

    **⚡ Quick Start:** Upload video → Click **Start Tracking Now!**
    """)

    gr.Markdown("**Reminder:** 🟢 Supports single human-centered video (≤3 s).")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📂 Select Video")
            video_input = gr.Video(label="Upload Video", format="mp4",
                                   height=250, elem_id="video_input")

            gr.Markdown("🎨 **Examples:** (scroll horizontally)")
            with gr.Row(elem_classes=["horizontal-examples"]):
                gr.Examples(
                    examples=[
                        ["example/me_tsl.mp4"],
                        ["example/eat_tsl.mp4"],
                        ["example/fried_rice_tsl.mp4"],
                        ["example/happy_tsl.mp4"],
                        ["example/angry_tsl.mp4"],
                    ],
                    inputs=[video_input],
                    cache_examples=False,
                    label="",
                    examples_per_page=6,
                )

        with gr.Column(scale=2):
            gr.Markdown("### ✨ Human Mesh Visualization")
            viz_video = gr.Video(
                label="Reconstructed Human Mesh Video",
                height=650, elem_id="viz_container",
                interactive=False, autoplay=False, sources=None,
            )

    with gr.Row():
        launch_btn    = gr.Button("🚀 Start Tracking Now!", variant="primary", size="lg")
        clear_all_btn = gr.Button("🗑️ Clear All", variant="secondary", size="sm")

    parameters_download = gr.File(label="📄 Download Mesh Results", interactive=False)

    gr.HTML("""
    <div style='background:linear-gradient(135deg,#e8eaff,#f0f2ff);border-radius:8px;
                padding:20px;margin:15px 0;text-align:center;
                border:1px solid rgba(102,126,234,0.15);'>
        <h3 style='color:#4a5568;margin:0 0 10px'>⭐ Love PEAR? Give us a Star! ⭐</h3>
        <a href="https://wujh2001.github.io/PEAR/" target="_blank"
           style='display:inline-flex;align-items:center;gap:8px;
                  background:rgba(102,126,234,0.1);color:#4a5568;padding:10px 20px;
                  border-radius:25px;text-decoration:none;font-weight:bold;font-size:14px;
                  border:1px solid rgba(102,126,234,0.2);'>
            ⭐ Star PEAR on GitHub
        </a>
    </div>
    """)

    gr.HTML("<div style='text-align:center;margin:20px 0;color:#888;font-size:12px;font-style:italic;'>"
            "Powered by PEAR | Built with ❤️ for the Computer Vision Community</div>")

    original_image_state = gr.State(None)

    video_input.change(fn=handle_video_upload, inputs=[video_input],
                       outputs=[original_image_state], api_name=False)
    launch_btn.click(fn=launch_viz, inputs=[original_image_state],
                     outputs=[viz_video, parameters_download], api_name=False)


if __name__ == "__main__":
    print("🌟 Launching PEAR...")
    demo.queue().launch()
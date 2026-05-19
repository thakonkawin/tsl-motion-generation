import argparse
import datetime
import os
import os.path as osp
import pickle
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.backends.cudnn as cudnn
import torchvision.transforms as transforms
from app.base import Tester
from app.config import Config
from human_models.human_models import SMPLX
from tqdm import tqdm
from ultralytics import YOLO
from utils.data_utils import generate_patch_image, load_img, process_bbox
from utils.inference_utils import non_max_suppression
from utils.visualization_utils import render_mesh


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_gpus", type=int, dest="num_gpus")
    parser.add_argument("--file_name", type=str, default="test")
    parser.add_argument("--ckpt_name", type=str, default="model_dump")
    parser.add_argument("--start", type=str, default=1)
    parser.add_argument("--end", type=str, default=1)
    parser.add_argument("--multi_person", action="store_true")
    args = parser.parse_args()
    return args


def save_smplx_params_correct(out, save_path):

    def to_np(x):
        return x.detach().cpu().numpy()

    global_orient = to_np(out["smplx_root_pose"]).reshape(1, 3).astype(np.float32)

    global_orient[:, 0] += np.pi  # flip 180° around X

    data = {
        "global_orient": global_orient,
        "body_pose": to_np(out["smplx_body_pose"]).reshape(1, -1).astype(np.float32),
        "left_hand_pose": to_np(out["smplx_lhand_pose"])
        .reshape(1, -1)
        .astype(np.float32),
        "right_hand_pose": to_np(out["smplx_rhand_pose"])
        .reshape(1, -1)
        .astype(np.float32),
        "betas": to_np(out["smplx_shape"]).reshape(1, -1).astype(np.float32),
        "expression": to_np(out["smplx_expr"]).reshape(1, -1).astype(np.float32),
        "transl": np.zeros((1, 3), dtype=np.float32),
        "gender": "neutral",
        "jaw_pose": to_np(out["smplx_jaw_pose"]).reshape(1, 3).astype(np.float32),
        "leye_pose": np.zeros((1, 3), dtype=np.float32),
        "reye_pose": np.zeros((1, 3), dtype=np.float32),
    }

    with open(save_path, "wb") as f:
        pickle.dump(data, f)


def inspect_smplx_output(out):

    def to_np(x):
        return x.detach().cpu().numpy()

    print("\n================ SMPL-X OUTPUT ================")

    for k, v in out.items():
        print(f"\n🔹 Key: {k}")
        print(f"   Type: {type(v)}")

        if torch.is_tensor(v):
            v = to_np(v)
            print(f"   Shape: {v.shape}")
            print(f"   Dtype: {v.dtype}")
            print(f"   Min: {v.min():.4f}  Max: {v.max():.4f}")
        else:
            print(f"   Value: {v}")

    print("==============================================\n")


def main():
    args = parse_args()
    cudnn.benchmark = True

    # init config
    time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    root_dir = Path(__file__).resolve().parent.parent
    config_path = osp.join(
        "./SMPLest-X/pretrained_models", args.ckpt_name, "config_base.py"
    )
    cfg = Config.load_config(config_path)
    checkpoint_path = osp.join(
        "./SMPLest-X/pretrained_models", args.ckpt_name, f"{args.ckpt_name}.pth.tar"
    )
    # change
    img_folder = osp.join("./tmp", "input_frames", args.file_name)
    output_folder = osp.join("./tmp", "output_frames", args.file_name)
    os.makedirs(output_folder, exist_ok=True)
    exp_name = f"inference_{args.file_name}_{args.ckpt_name}_{time_str}"

    # add-nmew
    param_folder = osp.join("./tmp", "smplx_params", args.file_name)
    os.makedirs(param_folder, exist_ok=True)

    new_config = {
        "model": {
            "pretrained_model_path": checkpoint_path,
        },
        "log": {
            "exp_name": exp_name,
            "log_dir": osp.join("./tmp/outputs", exp_name, "log"),
        },
    }
    cfg.update_config(new_config)
    cfg.prepare_log()

    # init human models
    smpl_x = SMPLX(cfg.model.human_model_path)

    # init tester
    demoer = Tester(cfg)
    demoer.logger.info(f"Using 1 GPU.")
    demoer.logger.info(
        f"Inference [{args.file_name}] with [{cfg.model.pretrained_model_path}]."
    )
    demoer._make_model()

    # init detector
    bbox_model = getattr(
        cfg.inference.detection,
        "model_path",
        "./SMPLest-X/pretrained_models/yolov8x.pt",
    )
    detector = YOLO(bbox_model)

    start = int(args.start)
    end = int(args.end) + 1

    for frame in tqdm(range(start, end)):
        # prepare input image
        img_path = osp.join(img_folder, f"{int(frame):06d}.jpg")

        transform = transforms.ToTensor()
        original_img = load_img(img_path)
        vis_img = original_img.copy()
        original_img_height, original_img_width = original_img.shape[:2]

        # detection, xyxy
        yolo_bbox = (
            detector.predict(
                original_img,
                device="cuda",
                classes=00,
                conf=cfg.inference.detection.conf,
                save=cfg.inference.detection.save,
                verbose=cfg.inference.detection.verbose,
            )[0]
            .boxes.xyxy.detach()
            .cpu()
            .numpy()
        )

        if len(yolo_bbox) < 1:
            # save original image if no bbox
            num_bbox = 0
        elif not args.multi_person:
            # only select the largest bbox
            num_bbox = 1
            # yolo_bbox = yolo_bbox[0]
        else:
            # keep bbox by NMS with iou_thr
            yolo_bbox = non_max_suppression(yolo_bbox, cfg.inference.detection.iou_thr)
            num_bbox = len(yolo_bbox)

        # loop all detected bboxes
        for bbox_id in range(num_bbox):
            yolo_bbox_xywh = np.zeros((4))
            yolo_bbox_xywh[0] = yolo_bbox[bbox_id][0]
            yolo_bbox_xywh[1] = yolo_bbox[bbox_id][1]
            yolo_bbox_xywh[2] = abs(yolo_bbox[bbox_id][2] - yolo_bbox[bbox_id][0])
            yolo_bbox_xywh[3] = abs(yolo_bbox[bbox_id][3] - yolo_bbox[bbox_id][1])

            # xywh
            bbox = process_bbox(
                bbox=yolo_bbox_xywh,
                img_width=original_img_width,
                img_height=original_img_height,
                input_img_shape=cfg.model.input_img_shape,
                ratio=getattr(cfg.data, "bbox_ratio", 1.25),
            )
            img, _, _ = generate_patch_image(
                cvimg=original_img,
                bbox=bbox,
                scale=1.0,
                rot=0.0,
                do_flip=False,
                out_shape=cfg.model.input_img_shape,
            )

            img = transform(img.astype(np.float32)) / 255
            img = img.cuda()[None, :, :, :]
            inputs = {"img": img}
            targets = {}
            meta_info = {}

            # mesh recovery
            with torch.no_grad():
                out = demoer.model(inputs, targets, meta_info, "test")
            # add-new
            param_path = osp.join(param_folder, f"frame_{int(frame):06d}.pkl")
            save_smplx_params_correct(out, param_path)
            # inspect_smplx_output(out)

            mesh = out["smplx_mesh_cam"].detach().cpu().numpy()[0]

            # render mesh
            focal = [
                cfg.model.focal[0] / cfg.model.input_body_shape[1] * bbox[2],
                cfg.model.focal[1] / cfg.model.input_body_shape[0] * bbox[3],
            ]
            princpt = [
                cfg.model.princpt[0] / cfg.model.input_body_shape[1] * bbox[2]
                + bbox[0],
                cfg.model.princpt[1] / cfg.model.input_body_shape[0] * bbox[3]
                + bbox[1],
            ]

            # draw the bbox on img
            vis_img = cv2.rectangle(
                vis_img,
                (int(yolo_bbox[bbox_id][0]), int(yolo_bbox[bbox_id][1])),
                (int(yolo_bbox[bbox_id][2]), int(yolo_bbox[bbox_id][3])),
                (0, 255, 0),
                1,
            )
            # draw mesh
            vis_img = render_mesh(
                vis_img,
                mesh,
                smpl_x.face,
                {"focal": focal, "princpt": princpt},
                mesh_as_vertices=False,
            )

        # save rendered image
        frame_name = os.path.basename(img_path)
        cv2.imwrite(os.path.join(output_folder, frame_name), vis_img[:, :, ::-1])


if __name__ == "__main__":
    main()

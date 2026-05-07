


## Install generate
```bash
bash scripts/install_gen.sh
```

## Install render
```bash
bash scripts/install_render.sh
```

## Extract 
```bash
bash scripts/inference_smplestx.sh smplest_x_h upload/videos/me_tsl.mp4 50
```



python inspect_pkl.py ./POSA_rp_poses/rp_carla_posed_002_0_0.pkl

python inspect_pkl.py ./smplx_params/frame_0004.pkl



นี่คือฟังก์ชันบันทึกข้อมูลที่ inference ได้ จาก วิดีโอแต่ละเฟรม 
def save_smplx_params_correct(out, save_path):

    def to_np(x):
        return x.detach().cpu().numpy()

    global_orient = to_np(out['smplx_root_pose']).reshape(1, 3).astype(np.float32)

    global_orient[:, 0] += np.pi   # flip 180° around X

    data = {
        'global_orient': global_orient,
        'body_pose': to_np(out['smplx_body_pose']).reshape(1, -1).astype(np.float32),
        'left_hand_pose': to_np(out['smplx_lhand_pose']).reshape(1, -1).astype(np.float32),
        'right_hand_pose': to_np(out['smplx_rhand_pose']).reshape(1, -1).astype(np.float32),
        'betas': to_np(out['smplx_shape']).reshape(1, -1).astype(np.float32),
        'expression': to_np(out['smplx_expr']).reshape(1, -1).astype(np.float32),
        'transl': np.zeros((1, 3), dtype=np.float32),
        'gender': 'neutral',
        'jaw_pose': to_np(out['smplx_jaw_pose']).reshape(1, 3).astype(np.float32),
        'leye_pose': np.zeros((1, 3), dtype=np.float32),
        'reye_pose': np.zeros((1, 3), dtype=np.float32),
    }

    with open(save_path, 'wb') as f:
        pickle.dump(data, f)

ข้อมูลจะถูกบันทึกที่ /tmp/smplx_params/{vid}/frame_000001.pkl........ n frame
ช่วยเขียนฟังก์ชันอ่านข้อมูลข้างต้น เพื่อบันทึกลงใน h5 สำหรับเตรียม datasets

tsl_dataset_v1.h5
│
│   ├── 1379b194-6c02-4a64-8dd3-5235c2bb781f
│   │   │
│   │   ├── smplx/
│   │   │   ├── betas (10,)
│   │   │   ├── global_orient (178, 3)
│   │   │   ├── body_pose (178, 63)
│   │   │   ├── left_hand_pose (178, 45)
│   │   │   ├── right_hand_pose (178, 45)
│   │   │   ├── jaw_pose (178, 3)
│   │   │   ├── leye_pose (178, 3)
│   │   │   ├── reye_pose (178, 3)
│   │   │   └── transl (178, 3)
│   │
│   │   ├── keypoints_2d/
│   │   │   ├── pose (178, 17, 3)
│   │   │   ├── left_hand (178, 21, 3)
│   │   │   ├── right_hand (178, 21, 3)
│   │   │   ├── face (178, 68, 3)
│   │   │   └── foot (178, 6, 3)
│   │
│   │   


แล้วหลังจากบันทึกใน h5 เสร็จแล้วให้บันทึกเพิ่มใน metadata.csv

def save_data(params_path, vid, gloss, fps, num_frames, frame_start, frame_end):
    return
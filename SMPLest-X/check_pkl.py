import pickle
import numpy as np
import sys
import os


def inspect_pkl(pkl_path):
    print(f"\n📦 Loading: {pkl_path}")

    # 🔒 กันไฟล์เสีย
    if not os.path.exists(pkl_path):
        print("❌ File not found")
        return

    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
    except Exception as e:
        print("❌ Failed to load pickle:", e)
        return

    # 🔍 print keys
    print("\nTop-level keys:", list(data.keys()))

    # 🔍 inspect ทีละ key
    for k, v in data.items():
        print(f"\n🔹 Key: {k}")
        print(f"   Type: {type(v)}")

        if isinstance(v, np.ndarray):
            print(f"   Shape: {v.shape}")
            print(f"   Dtype: {v.dtype}")

            if v.size > 0:
                print(f"   Min: {v.min():.4f}  Max: {v.max():.4f}")
        else:
            print(f"   Value: {v}")

    return data


def validate_smplx(data):
    print("\n🧪 Validating SMPL-X format...")

    try:
        assert data['global_orient'].shape == (1, 3)
        assert data['body_pose'].shape == (1, 63)
        assert data['left_hand_pose'].shape == (1, 45)
        assert data['right_hand_pose'].shape == (1, 45)
        assert data['jaw_pose'].shape == (1, 3)
        assert data['leye_pose'].shape == (1, 3)
        assert data['reye_pose'].shape == (1, 3)
        assert data['transl'].shape == (1, 3)

        assert data['betas'].shape[1] == 10
        assert data['expression'].shape[1] == 10

        assert isinstance(data['gender'], str)

        print("✅ SMPL-X format is VALID")

    except AssertionError as e:
        print("❌ Format INVALID:", e)


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_pkl.py path/to/file.pkl")
        return

    pkl_path = sys.argv[1]

    data = inspect_pkl(pkl_path)

    if data is not None:
        validate_smplx(data)


if __name__ == "__main__":
    main()

    # python check_pkl.py ./demo/smplx_params/angry_tsl/frame_000001.pkl

    # sh scripts/inference_1.sh smplest_x_h happy_tsl.mp4 50
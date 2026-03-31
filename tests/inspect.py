import pickle
import numpy as np
import torch
import sys


def inspect_value(key, value):
    print(f"\n🔹 Key: {key}")
    print(f"   Type: {type(value)}")

    if isinstance(value, np.ndarray):
        print(f"   Shape: {value.shape}")
        print(f"   Dtype: {value.dtype}")
        print(f"   Min: {value.min():.4f}  Max: {value.max():.4f}")

    elif isinstance(value, torch.Tensor):
        print(f"   Shape: {tuple(value.shape)}")
        print(f"   Dtype: {value.dtype}")
        print(f"   Device: {value.device}")
        print(f"   Min: {value.min().item():.4f}  Max: {value.max().item():.4f}")

    elif isinstance(value, list):
        print(f"   List length: {len(value)}")
        if len(value) > 0:
            print(f"   First element type: {type(value[0])}")

    elif isinstance(value, dict):
        print(f"   Nested dict with keys: {list(value.keys())}")

    else:
        print(f"   Value preview: {value}")


def main(pkl_path):
    print(f"\n📂 Loading: {pkl_path}")

    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    print("\n==============================")
    print("PKL CONTENT SUMMARY")
    print("==============================")

    if isinstance(data, dict):
        print(f"\nTop-level keys: {list(data.keys())}")

        for key, value in data.items():
            inspect_value(key, value)

    else:
        print("File is NOT a dict.")
        print(f"Type: {type(data)}")
        inspect_value("root_object", data)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("   python inspect_pkl.py your_file.pkl")
        sys.exit(1)

    main(sys.argv[1])

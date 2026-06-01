
conda create -n sapiens2 python=3.12 -y
conda activate sapiens2

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

pip install -e .


hf download facebook/sapiens2-pose-1b sapiens2_1b_pose.safetensors
    --local-dir ~/sapiens2_host/pose

hf download facebook/detr-resnet-101-dc5 \
    --local-dir "/home/thakon/workspaces/sapiens2/sapiens2_host/detector/detr-resnet-101-dc5"


bash sapiens2/sapiens/pose/scripts/demo/keypoints308.sh

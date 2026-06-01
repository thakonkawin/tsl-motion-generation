#!/usr/bin/env bash
set -e

source ~/anaconda3/etc/profile.d/conda.sh

conda create -n sapiens python=3.10
conda activate sapiens

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install opencv-python tqdm json-tricks

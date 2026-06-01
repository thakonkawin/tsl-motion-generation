#!/usr/bin/env bash
set -e

source ~/anaconda3/etc/profile.d/conda.sh

conda create -n smplestx -c conda-forge python=3.9.22 -y
conda activate smplestx

python -m pip install --upgrade pip setuptools wheel

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements_smplestx.txt
pip install --extra-index-url https://miropsota.github.io/torch_packages_builder pytorch3d==0.7.8+pt2.8.0cu128
pip install chumpy --no-build-isolation

#!/usr/bin/env bash
set -e

source ~/anaconda3/etc/profile.d/conda.sh

conda create -n tsl-render python=3.11 -y
conda activate tsl-render

pip install -r scripts/requirements_render.txt

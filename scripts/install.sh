#!/usr/bin/env bash
set -e

source ~/anaconda3/etc/profile.d/conda.sh

conda create -n tsl-gen python=3.13 -y
conda activate tsl-gen

pip install -r requirements.txt

pip install -e ./sapiens2

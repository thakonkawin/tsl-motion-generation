#!/bin/bash

# -------------------------------------------------------
# กำหนด SAPIENS_ROOT = root ของ repo ที่ clone มา
# สคริปต์นี้วางไว้ที่ไหนก็ได้ — แก้ SAPIENS_ROOT ตรงนี้
# -------------------------------------------------------
# SAPIENS_ROOT="$(cd "$(dirname "$(realpath "$0")")" && pwd)"
SAPIENS_ROOT="$(cd "$(dirname "$(realpath "$0")")/../../../.." && pwd)"

# -------------------------------------------------------
# paths หลัก (ปรับได้)
# -------------------------------------------------------
SAPIENS_CHECKPOINT_ROOT="${SAPIENS_ROOT}/sapiens2_host"
INPUT="${SAPIENS_ROOT}/example"
OUTPUT="${SAPIENS_ROOT}/outputs"

# -------------------------------------------------------
# Pose model
# -------------------------------------------------------
MODEL_NAME="sapiens2_1b"
DATASET="shutterstock_goliath_3po"
CHECKPOINT="${SAPIENS_CHECKPOINT_ROOT}/pose/${MODEL_NAME}_pose.safetensors"
CONFIG_FILE="${SAPIENS_ROOT}/sapiens/pose/configs/keypoints308/${DATASET}/${MODEL_NAME}_keypoints308_${DATASET}-1024x768.py"

# -------------------------------------------------------
# Detector (DETR)
# -------------------------------------------------------
DET_CONFIG="${SAPIENS_ROOT}/sapiens/det/configs/detr/detr_r101_dc5_8x2_150e_coco.py"
DET_CHECKPOINT="${SAPIENS_CHECKPOINT_ROOT}/detector/detr-resnet-101-dc5"

# -------------------------------------------------------
# Visualization options
# -------------------------------------------------------
LINE_THICKNESS=8
RADIUS=6
KPT_THRES=0.3

# -------------------------------------------------------
# Multi-GPU
# -------------------------------------------------------
RUN_FILE="${SAPIENS_ROOT}/sapiens/pose/tools/vis/vis_pose.py"
JOBS_PER_GPU=1
GPU_IDS=(0)
TOTAL_JOBS=$((JOBS_PER_GPU * ${#GPU_IDS[@]}))

# -------------------------------------------------------
# สร้าง output dir
# -------------------------------------------------------
mkdir -p "${OUTPUT}"

# -------------------------------------------------------
# สร้าง image list
# -------------------------------------------------------
IMAGE_LIST="${INPUT}/image_list.txt"
find "${INPUT}" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) \
  | sort > "${IMAGE_LIST}"

if [ ! -s "${IMAGE_LIST}" ]; then
  echo "[ERROR] No images found in: ${INPUT}"
  exit 1
fi

NUM_IMAGES=$(wc -l < "${IMAGE_LIST}")
echo "[INFO] Found ${NUM_IMAGES} images"

# -------------------------------------------------------
# แบ่งงานให้แต่ละ GPU
# -------------------------------------------------------
IMAGES_PER_JOB=$((NUM_IMAGES / TOTAL_JOBS))
EXTRA_IMAGES=$((NUM_IMAGES % TOTAL_JOBS))
current_line=1

for ((i=0; i<TOTAL_JOBS; i++)); do
  TEXT_FILE="${INPUT}/image_paths_$((i+1)).txt"
  if [ $i -lt $EXTRA_IMAGES ]; then
    images_for_this_job=$((IMAGES_PER_JOB + 1))
  else
    images_for_this_job=$IMAGES_PER_JOB
  fi

  if [ $images_for_this_job -gt 0 ]; then
    sed -n "${current_line},$((current_line + images_for_this_job - 1))p" \
      "${IMAGE_LIST}" > "${TEXT_FILE}"
    current_line=$((current_line + images_for_this_job))
  else
    touch "${TEXT_FILE}"
  fi
done

# -------------------------------------------------------
# รัน inference
# -------------------------------------------------------
for ((i=0; i<TOTAL_JOBS; i++)); do
  GPU_ID=${GPU_IDS[$((i % ${#GPU_IDS[@]}))]}
  TEXT_FILE="${INPUT}/image_paths_$((i+1)).txt"

  echo "[INFO] Job $((i+1))/${TOTAL_JOBS} → GPU ${GPU_ID}"

  # เพิ่ม cd เข้า sapiens/pose ก่อน แล้วใช้ path สัมบูรณ์ทั้งหมด
  (
    cd "${SAPIENS_ROOT}/sapiens/pose" || exit 1
    CUDA_VISIBLE_DEVICES=${GPU_ID} python "${RUN_FILE}" \
      "${DET_CHECKPOINT}" \
      "${CONFIG_FILE}" \
      "${CHECKPOINT}" \
      --input "${TEXT_FILE}" \
      --output "${OUTPUT}" \
      --radius ${RADIUS} \
      --kpt-thr ${KPT_THRES} \
      --thickness ${LINE_THICKNESS}
  ) &
done

wait
echo "[DONE] Results saved to: ${OUTPUT}"

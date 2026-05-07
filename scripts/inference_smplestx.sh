#!/usr/bin/env bash
set -e

CKPT_NAME=$1
VIDEO_PATH=$2
FPS=${3:-30}

# 🔥 หา root ของ smplest_x
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# 🔥 normalize path
VIDEO_PATH="$(realpath "$VIDEO_PATH")"

FILE_NAME="$(basename "$VIDEO_PATH")"
NAME="${FILE_NAME%.*}"
EXT="${FILE_NAME##*.}"

# 🔥 เปลี่ยน output ไปที่ core (optional)
CORE_DIR="$(dirname "$ROOT_DIR")/core"

IMG_PATH="$ROOT_DIR/tmp/input_frames/$NAME"
OUTPUT_PATH="$ROOT_DIR/tmp/output_frames/$NAME"

mkdir -p "$IMG_PATH"
mkdir -p "$OUTPUT_PATH"

echo "[INFO] Video: $VIDEO_PATH"
echo "[INFO] Working dir: $ROOT_DIR"

# -------- convert video to frames --------
case "$EXT" in
    mp4|avi|mov|mkv|flv|wmv|webm|mpeg|mpg)
        ffmpeg -i "$VIDEO_PATH" -f image2 -vf fps=${FPS}/1 -qscale 0 "$IMG_PATH/%06d.jpg"
        ;;
    jpg|jpeg|png|bmp|gif|tiff|tif|webp|svg)
        cp "$VIDEO_PATH" "$IMG_PATH/000001.$EXT"
        ;;
    *)
        echo "Unknown file type: $EXT"
        exit 1
        ;;
esac

END_COUNT=$(find "$IMG_PATH" -type f | wc -l)

# -------- inference --------
# PYTHONPATH="$ROOT_DIR/SMPLest-X:$PYTHONPATH" \
# conda run -n smplestx_v3 python "$ROOT_DIR/SMPLest-X/main/inference.py" \
#     --num_gpus 1 \
#     --file_name "$NAME" \
#     --ckpt_name "$CKPT_NAME" \
#     --end "$END_COUNT"
cd "$ROOT_DIR" && \
PYTHONPATH="$ROOT_DIR/SMPLest-X:$PYTHONPATH" \
conda run -n smplestx_v3 --no-capture-output \
    python "$ROOT_DIR/SMPLest-X/main/inference.py" \
    --num_gpus 1 \
    --file_name "$NAME" \
    --ckpt_name "$CKPT_NAME" \
    --end "$END_COUNT"

# -------- convert frames to video --------
RESULT_PATH="$ROOT_DIR/tmp/mesh/result_${NAME}.mp4"
mkdir -p "$(dirname "$RESULT_PATH")"

case "$EXT" in
    mp4|avi|mov|mkv|flv|wmv|webm|mpeg|mpg)
        ffmpeg -y -f image2 -r ${FPS} -i "$OUTPUT_PATH/%06d.jpg" \
            -c:v libx264 -pix_fmt yuv420p -crf 18 -preset fast "$RESULT_PATH"
        ;;
    *)
        cp "$OUTPUT_PATH/000001.$EXT" "$CORE_DIR/outputs/result_$FILE_NAME"
        ;;
esac

# -------- cleanup --------
# rm -rf "$ROOT_DIR/tmp"

echo "[DONE] Output: $RESULT_PATH"
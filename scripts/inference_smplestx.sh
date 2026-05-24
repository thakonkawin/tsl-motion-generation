#!/usr/bin/env bash
set -e

CKPT_NAME=$1
VIDEO_PATH=$2
FPS=${3:-30}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
SMPLX_DIR="$ROOT_DIR/SMPLest-X"

VIDEO_PATH="$(realpath "$VIDEO_PATH")"

FILE_NAME="$(basename "$VIDEO_PATH")"
NAME="${FILE_NAME%.*}"
EXT="${FILE_NAME##*.}"
EXT_LOWER="${EXT,,}"

IMG_PATH="$ROOT_DIR/tmp/input_frames/$NAME"
OUTPUT_PATH="$ROOT_DIR/tmp/output_frames/$NAME"
RESULT_PATH="$ROOT_DIR/tmp/mesh/result_${NAME}.mp4"

mkdir -p "$IMG_PATH"
mkdir -p "$OUTPUT_PATH"
mkdir -p "$(dirname "$RESULT_PATH")"

echo "[INFO] Video: $VIDEO_PATH"
echo "[INFO] Root dir: $ROOT_DIR"
echo "[INFO] SMPLest-X dir: $SMPLX_DIR"

# -------- activate conda env --------
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate smplestx_v3

# -------- clean old files --------
rm -rf "$IMG_PATH"/*
rm -rf "$OUTPUT_PATH"/*

# -------- convert input to frames --------
case "$EXT_LOWER" in
    mp4|avi|mov|mkv|flv|wmv|webm|mpeg|mpg)
        echo "[INFO] Extracting frames..."

        ffmpeg -y \
            -i "$VIDEO_PATH" \
            -vf "fps=${FPS}" \
            -q:v 1 \
            "$IMG_PATH/%06d.jpg"
        ;;

    jpg|jpeg|png|bmp|gif|tiff|tif|webp)
        echo "[INFO] Single image input detected..."

        cp "$VIDEO_PATH" "$IMG_PATH/000001.jpg"
        ;;

    *)
        echo "[ERROR] Unsupported file type: $EXT"
        exit 1
        ;;
esac

END_COUNT=$(find "$IMG_PATH" -type f | wc -l)

if [ "$END_COUNT" -eq 0 ]; then
    echo "[ERROR] No frames extracted"
    exit 1
fi

echo "[INFO] Total frames: $END_COUNT"




# -------- inference --------
echo "[INFO] Running SMPLest-X inference..."

cd "$ROOT_DIR"

export PYTHONPATH="$SMPLX_DIR"

python "$SMPLX_DIR/main/inference.py" \
    --num_gpus 1 \
    --file_name "$NAME" \
    --ckpt_name "$CKPT_NAME" \
    --end "$END_COUNT"


# -------- render output --------
case "$EXT_LOWER" in
    mp4|avi|mov|mkv|flv|wmv|webm|mpeg|mpg)

        echo "[INFO] Rendering video..."

        ffmpeg -y \
            -framerate "$FPS" \
            -i "$OUTPUT_PATH/%06d.jpg" \
            -c:v libx264 \
            -pix_fmt yuv420p \
            -crf 18 \
            -preset fast \
            "$RESULT_PATH"

        echo "[DONE] Output: $RESULT_PATH"
        ;;

    *)
        RESULT_IMAGE="$ROOT_DIR/tmp/mesh/result_${FILE_NAME}"

        cp "$OUTPUT_PATH/000001.jpg" "$RESULT_IMAGE"

        echo "[DONE] Output: $RESULT_IMAGE"
        ;;
esac

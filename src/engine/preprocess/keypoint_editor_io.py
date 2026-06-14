"""โหลด/บันทึกข้อมูล keypoints สำหรับ pose editor บนหน้า preprocess

- ``build_editor_payload`` อ่าน keypoints_data.json ของเฟรมที่เลือก + รูปภาพต้นฉบับ
  แล้วประกอบเป็น payload (JSON string) ส่งให้ editor ฝั่ง frontend
- ``apply_edits`` รับผลการแก้ไขกลับมาเขียนทับ keypoints_data.json
"""

import base64
import json
import os
from pathlib import Path

from src.engine.preprocess import keypoint_layout as layout
from src.utils.config import AppConfig
from src.utils.logger import Logger

KEYPOINTS_JSON_NAME = "keypoints_data.json"


class KeypointEditorIO:
    def __init__(self) -> None:
        self._cfg = AppConfig()
        self._logger = Logger()

    def _json_path(self, video_id: str) -> Path:
        return self._cfg.get_path(
            self._cfg.TMP_KEYPOINT_DIR / video_id / KEYPOINTS_JSON_NAME
        )

    def _load_json(self, video_id: str) -> dict:
        json_path = self._json_path(video_id)

        if not json_path.exists():
            msg = f"keypoints_data.json not found: {json_path}"
            self._logger.error(message=msg, module="KeypointEditorIO._load_json")
            raise FileNotFoundError(msg)

        with json_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _sorted_frames(self, data: dict) -> list[dict]:
        return sorted(data.get("frames", []), key=lambda fr: fr["image_name"])

    def _image_data_url(self, video_id: str, image_name: str) -> str:
        """ใช้รูปเฟรมต้นฉบับ (ไม่มี skeleton วาดทับ) ถ้าไม่มีค่อย fallback ไปรูป keypoint"""
        candidates = [
            self._cfg.get_path(
                self._cfg.TMP_UPLOAD_FRAME_DIR / video_id / image_name
            ),
            self._cfg.get_path(self._cfg.TMP_KEYPOINT_DIR / video_id / image_name),
        ]
        for path in candidates:
            if path.exists():
                raw = base64.b64encode(path.read_bytes()).decode("ascii")
                mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
                return f"data:{mime};base64,{raw}"

        msg = f"frame image not found for {video_id}/{image_name}"
        self._logger.error(message=msg, module="KeypointEditorIO._image_data_url")
        raise FileNotFoundError(msg)

    def build_editor_payload(self, video_id: str, frame_index: int) -> str:
        data = self._load_json(video_id)
        frames = self._sorted_frames(data)

        if not (0 <= frame_index < len(frames)):
            raise IndexError(f"frame_index {frame_index} out of range ({len(frames)})")

        frame = frames[frame_index]
        instances = frame.get("instances", [])
        if not instances:
            raise ValueError(f"no person detected in frame {frame['image_name']}")

        keypoints = instances[0]["keypoints"]

        joints = [
            {
                "i": idx,
                "name": layout.POSE_HAND_NAMES[idx],
                "group": layout.POSE_HAND_GROUPS[idx],
                "x": keypoints[idx][0],
                "y": keypoints[idx][1],
            }
            for idx in range(layout.POSE_HAND_COUNT)
        ]

        payload = {
            "video_id": video_id,
            "frame_index": frame_index,
            "image_name": frame["image_name"],
            "image": self._image_data_url(video_id, frame["image_name"]),
            "image_size": data.get("image_size", [600, 600]),
            "joints": joints,
            "edges": layout.POSE_HAND_EDGES,
        }
        return json.dumps(payload)

    def apply_edits(self, result_json: str) -> None:
        result = json.loads(result_json)
        video_id = result["video_id"]
        image_name = result["image_name"]
        edits = result.get("edits", [])

        if not edits:
            return

        data = self._load_json(video_id)

        frame = next(
            (fr for fr in data["frames"] if fr["image_name"] == image_name), None
        )
        if frame is None or not frame.get("instances"):
            raise ValueError(f"frame {image_name} not found in dataset")

        instance = frame["instances"][0]
        keypoints = instance["keypoints"]
        scores = instance.get("keypoint_scores")

        for edit in edits:
            idx = int(edit["i"])
            keypoints[idx] = [float(edit["x"]), float(edit["y"])]
            # joint ที่ผู้ใช้ย้ายเอง ถือว่า valid เต็มที่ (กรณีครึ่งตัวที่ score เดิมต่ำ)
            if scores is not None and 0 <= idx < len(scores):
                scores[idx] = 1.0

        json_path = self._json_path(video_id)
        tmp_path = json_path.with_suffix(".json.tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp_path, json_path)

        self._logger.info(
            message=f"updated {len(edits)} joints in {image_name}",
            module="KeypointEditorIO.apply_edits",
        )

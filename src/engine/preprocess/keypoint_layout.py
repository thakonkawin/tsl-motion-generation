"""Layout ของ keypoints เฉพาะส่วน pose + hands (ไม่เอา face)

อ้างอิงลำดับ keypoint จาก sapiens2 (goliath 308 จุด) ตาม
``sapiens2/sapiens/pose/configs/_base_/keypoints308.py`` (dataset_info.keypoint_info)
โดย index 0-69 คือ body + แขน + มือทั้งสองข้าง + คอ ส่วน 70-307 เป็นใบหน้าซึ่งไม่นำมาแก้ไข
"""

# index -> ชื่อ joint (เฉพาะ 0-69 = pose + hands)
POSE_HAND_NAMES: dict[int, str] = {
    0: "nose",
    1: "left_eye",
    2: "right_eye",
    3: "left_ear",
    4: "right_ear",
    5: "left_shoulder",
    6: "right_shoulder",
    7: "left_elbow",
    8: "right_elbow",
    9: "left_hip",
    10: "right_hip",
    11: "left_knee",
    12: "right_knee",
    13: "left_ankle",
    14: "right_ankle",
    15: "left_big_toe",
    16: "left_small_toe",
    17: "left_heel",
    18: "right_big_toe",
    19: "right_small_toe",
    20: "right_heel",
    21: "right_thumb4",
    22: "right_thumb3",
    23: "right_thumb2",
    24: "right_thumb1",
    25: "right_forefinger4",
    26: "right_forefinger3",
    27: "right_forefinger2",
    28: "right_forefinger1",
    29: "right_middle_finger4",
    30: "right_middle_finger3",
    31: "right_middle_finger2",
    32: "right_middle_finger1",
    33: "right_ring_finger4",
    34: "right_ring_finger3",
    35: "right_ring_finger2",
    36: "right_ring_finger1",
    37: "right_pinky_finger4",
    38: "right_pinky_finger3",
    39: "right_pinky_finger2",
    40: "right_pinky_finger1",
    41: "right_wrist",
    42: "left_thumb4",
    43: "left_thumb3",
    44: "left_thumb2",
    45: "left_thumb1",
    46: "left_forefinger4",
    47: "left_forefinger3",
    48: "left_forefinger2",
    49: "left_forefinger1",
    50: "left_middle_finger4",
    51: "left_middle_finger3",
    52: "left_middle_finger2",
    53: "left_middle_finger1",
    54: "left_ring_finger4",
    55: "left_ring_finger3",
    56: "left_ring_finger2",
    57: "left_ring_finger1",
    58: "left_pinky_finger4",
    59: "left_pinky_finger3",
    60: "left_pinky_finger2",
    61: "left_pinky_finger1",
    62: "left_wrist",
    63: "left_olecranon",
    64: "right_olecranon",
    65: "left_cubital_fossa",
    66: "right_cubital_fossa",
    67: "left_acromion",
    68: "right_acromion",
    69: "neck",
}

# จำนวน joint ที่นำมาแก้ไข (index 0..POSE_HAND_COUNT-1)
POSE_HAND_COUNT = len(POSE_HAND_NAMES)

# กลุ่มของ joint สำหรับใช้แยกสีบน editor
_NAME_TO_INDEX = {name: idx for idx, name in POSE_HAND_NAMES.items()}


def _group_of(idx: int) -> str:
    if 21 <= idx <= 41:
        return "right_hand"
    if 42 <= idx <= 62:
        return "left_hand"
    if idx in (0, 1, 2, 3, 4, 69):
        return "head"
    return "body"


POSE_HAND_GROUPS: dict[int, str] = {
    idx: _group_of(idx) for idx in POSE_HAND_NAMES
}


def _finger_chain(side: str, finger: str) -> list[tuple[str, str]]:
    """ข้อต่อของนิ้ว: wrist -> 1 -> 2 -> 3 -> 4 (4 = ปลายนิ้ว)"""
    joints = [f"{side}_wrist"] + [f"{side}_{finger}{n}" for n in (1, 2, 3, 4)]
    return [(joints[i], joints[i + 1]) for i in range(len(joints) - 1)]


def _build_edges() -> list[tuple[int, int]]:
    pairs: list[tuple[str, str]] = [
        # head
        ("nose", "left_eye"),
        ("nose", "right_eye"),
        ("left_eye", "left_ear"),
        ("right_eye", "right_ear"),
        ("nose", "neck"),
        ("neck", "left_shoulder"),
        ("neck", "right_shoulder"),
        # torso + arms
        ("left_shoulder", "right_shoulder"),
        ("left_shoulder", "left_elbow"),
        ("left_elbow", "left_wrist"),
        ("right_shoulder", "right_elbow"),
        ("right_elbow", "right_wrist"),
        ("left_shoulder", "left_hip"),
        ("right_shoulder", "right_hip"),
        ("left_hip", "right_hip"),
        # legs + feet
        ("left_hip", "left_knee"),
        ("left_knee", "left_ankle"),
        ("right_hip", "right_knee"),
        ("right_knee", "right_ankle"),
        ("left_ankle", "left_big_toe"),
        ("left_ankle", "left_small_toe"),
        ("left_ankle", "left_heel"),
        ("right_ankle", "right_big_toe"),
        ("right_ankle", "right_small_toe"),
        ("right_ankle", "right_heel"),
    ]

    for side in ("left", "right"):
        for finger in (
            "thumb",
            "forefinger",
            "middle_finger",
            "ring_finger",
            "pinky_finger",
        ):
            pairs += _finger_chain(side, finger)

    edges: list[tuple[int, int]] = []
    for a, b in pairs:
        if a in _NAME_TO_INDEX and b in _NAME_TO_INDEX:
            edges.append((_NAME_TO_INDEX[a], _NAME_TO_INDEX[b]))
    return edges


POSE_HAND_EDGES: list[tuple[int, int]] = _build_edges()

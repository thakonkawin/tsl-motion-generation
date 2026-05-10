import smplx
import torch
import pyrender
import trimesh
import numpy as np

model = smplx.create(
    model_path="../models",
    model_type="smplx",
    gender="neutral",
    use_face_contour=True,
    num_expression_coeffs=10,
    use_pca=False,
)

# Batch size
batch_size = 1

# Shape parameters (10 default shape components)
betas = torch.zeros([batch_size, 10], dtype=torch.float32)

# Expression parameters (10 default expression components)
# แต่ละค่าเป็น PCA component ของ facial expression space
# (ไม่ได้หมายความว่า index 0 = ยิ้ม เสมอไป)
#
# ค่าอยู่ในหน่วย standard deviation (σ)
#
#  0.0  = ใบหน้าเป็นกลาง (neutral expression)
# +1.0  = เบี่ยงเบนจากค่าเฉลี่ย +1σ
# -1.0  = เบี่ยงเบนจากค่าเฉลี่ย -1σ
#
# ปกติใช้ช่วงประมาณ -3.0 ถึง +3.0
# แนะนำใช้งานจริงช่วง -2.0 ถึง +2.0
# หากเกิน ±3.0 อาจเกิดใบหน้าผิดธรรมชาติ (artifact)
#
# วิธีใช้งาน:
# - ต้องการใบหน้าเป็นกลาง → ใช้ 0.0 ทุกตัว
# - ต้องการแสดงอารมณ์เล็กน้อย → ปรับ ±0.5 ถึง ±1.0
# - ต้องการอารมณ์ชัดเจน → ปรับ ±1.5 ถึง ±2.0
# expression = torch.zeros([batch_size, 10], dtype=torch.float32)
expression = torch.tensor(
    [
        [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ]
    ],
    dtype=torch.float32,
)

# Pose parameters (in axis-angle format)
body_pose = torch.zeros([batch_size, model.NUM_BODY_JOINTS * 3], dtype=torch.float32)
global_orient = torch.zeros([batch_size, 3], dtype=torch.float32)
jaw_pose = torch.zeros([batch_size, 3], dtype=torch.float32)
left_hand_pose = torch.zeros(
    [batch_size, model.NUM_HAND_JOINTS * 3], dtype=torch.float32
)
right_hand_pose = torch.zeros(
    [batch_size, model.NUM_HAND_JOINTS * 3], dtype=torch.float32
)

output = model(
    betas=betas,
    expression=expression,
    body_pose=body_pose,
    global_orient=global_orient,
    jaw_pose=jaw_pose,
    left_hand_pose=left_hand_pose,
    right_hand_pose=right_hand_pose,
)

vertices = output.vertices[0].detach().cpu().numpy()
faces = model.faces
joints = output.joints.detach().cpu().numpy().squeeze()

vertex_colors = np.ones([vertices.shape[0], 4]) * [0.3, 0.3, 0.3, 0.8]
tri_mesh = trimesh.Trimesh(vertices, model.faces, vertex_colors=vertex_colors)
mesh = pyrender.Mesh.from_trimesh(tri_mesh)

# Create a scene and add the mesh
scene = pyrender.Scene()
scene.add(mesh)

# Show the visualization
pyrender.Viewer(scene, use_raymond_lighting=True)

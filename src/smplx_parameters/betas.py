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

# Shape parameters เป็นตัวกำหนดรูปร่าง (อ้วน, ผอม, สูง, เตี้ย)
# Gender ของแต่ละ model จะกำหนดค่า default เป็น 0 (0-9) เหมือนกันทั้งหมด
# แต่ละค่าเป็น PCA component ของรูปร่าง
# ค่าอยู่ในหน่วย standard deviation (σ)
#
#  0.0  = รูปร่างเฉลี่ยของ dataset
# +1.0  = เบี่ยงเบนจากค่าเฉลี่ย +1σ
# -1.0  = เบี่ยงเบนจากค่าเฉลี่ย -1σ
#
# ปกติใช้ช่วงประมาณ -3.0 ถึง +3.0
#
# วิธีใช้งาน:
# - ต้องการรูปร่างใกล้ค่าเฉลี่ยให้ใช้ 0.0 ทุกตัว
# - ต้องการรูปร่างแตกต่างเล็กน้อยให้ปรับ ±0.5 ถึง ±1.0
# - ต้องการรูปร่างชัดเจนมากให้ปรับ ±2.0 ขึ้นไป
# - ไม่ควรเกิน ±3.0 เพราะโมเดลจะเริ่มผิดธรรมชาติ
betas = torch.tensor(
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


expression = torch.zeros([batch_size, 10], dtype=torch.float32)
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

# Optionally visualize joints
if joints is not None:
    sm = trimesh.creation.uv_sphere(radius=0.005)
    sm.visual.vertex_colors = [0.9, 0.1, 0.1, 1.0]
    tfs = np.tile(np.eye(4), (len(joints), 1, 1))
    tfs[:, :3, 3] = joints
    joints_pcl = pyrender.Mesh.from_trimesh(sm, poses=tfs)
    scene.add(joints_pcl)

# Show the visualization
pyrender.Viewer(scene, use_raymond_lighting=True)

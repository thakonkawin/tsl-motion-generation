import smplx
import torch
import pyrender
import trimesh
import numpy as np
import math

model = smplx.create(
    model_path="../models",
    model_type="smplx",
    gender="neutral",
    use_face_contour=True,
    num_expression_coeffs=10,
    use_pca=False,
)

batch_size = 1
betas = torch.zeros([batch_size, 10], dtype=torch.float32)
expression = torch.zeros([batch_size, 10], dtype=torch.float32)
body_pose = torch.zeros([batch_size, model.NUM_BODY_JOINTS * 3], dtype=torch.float32)
# ควบคุมการหมุนโดยรวมของร่างกาย (root orientation)
# global_orient[:, 0] = การหมุนรอบแกน X
# global_orient[:, 1] = การหมุนรอบแกน Y
# global_orient[:, 2] = การหมุนรอบแกน Z
#
# ใช้ควบคุม:
# - ตัวละครหันไปทิศทางไหน
# - ให้โมเดลหันเข้ากล้อง
# - ปรับให้เหมาะกับ scene coordinate
global_orient = torch.tensor([[0.0, 0.0, 0.0]])
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
pelvis = joints[0]
vertices = vertices - pelvis
joints = joints - pelvis

vertex_colors = np.ones([vertices.shape[0], 4]) * [0.3, 0.3, 0.3, 0.8]
tri_mesh = trimesh.Trimesh(vertices, model.faces, vertex_colors=vertex_colors)
mesh = pyrender.Mesh.from_trimesh(tri_mesh)

scene = pyrender.Scene()
scene.add(mesh)


def look_at(eye, target, up=[0, 1, 0]):
    eye = np.array(eye)
    target = np.array(target)
    up = np.array(up)

    z = eye - target
    z /= np.linalg.norm(z)
    x = np.cross(up, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)

    pose = np.eye(4)
    pose[:3, 0] = x
    pose[:3, 1] = y
    pose[:3, 2] = z
    pose[:3, 3] = eye
    return pose


camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
camera_pose = look_at(eye=[0, 1.2, 2.5], target=[0, 1.0, 0])
scene.add(camera, pose=camera_pose)

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

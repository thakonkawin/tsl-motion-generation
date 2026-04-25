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

betas = torch.zeros([batch_size, 10], dtype=torch.float32)
expression = torch.zeros([batch_size, 10], dtype=torch.float32)

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

body_mapping = np.array(
    [
        # 0,  # pelvis
        # 2,  # right_hip
        # 1,  # left_hip
        # 3,  # spine1
        # 5,  # right_knee
        # 4,  # left_knee
        # 6,  # spine2
        # 8,  # right_ankle
        # 7,  # left_ankle
        # 9,  # spine3
        # 11,  # right_foot
        # 10,  # left_foot
        # 12,  # neck
        # 14,  # right_collar
        # 13,  # left_collar
        # 15,  # head
        # 17,  # right_shoulder
        # 16,  # left_shoulder
        # 19,  # right_elbow
        # 18,  # left_elbow
        # 21,  # right_wrist
        # 20,  # left_wrist
        55,
        12,
        17,
        19,
        21,
        16,
        18,
        20,
        0,
        2,
        5,
        8,
        1,
        4,
        7,
        56,
        57,
        58,
        59,
    ],
    dtype=np.int32,
)

# Optionally visualize ONLY body joints (remove hands & face)
if joints is not None:
    body_joints = joints[body_mapping]

    print(joints.shape)
    print(model.NUM_BODY_JOINTS)

    sm = trimesh.creation.uv_sphere(radius=0.01)
    sm.visual.vertex_colors = [0.9, 0.1, 0.1, 1.0]

    tfs = np.tile(np.eye(4), (len(body_joints), 1, 1))
    tfs[:, :3, 3] = body_joints

    joints_pcl = pyrender.Mesh.from_trimesh(sm, poses=tfs)
    scene.add(joints_pcl)
# Show the visualization
pyrender.Viewer(scene, use_raymond_lighting=True)

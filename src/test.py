# import h5py
# import numpy as np

# mode สำคัญ:

# 'w' = สร้างใหม่ (overwrite)
# 'a' = append (มีแล้วเปิด ไม่มีสร้าง)
# 'r' = read only


# สร้างไฟล์ใหม่ (เขียนทับถ้ามีอยู่แล้ว)
# with h5py.File('example.h5', 'w') as f:
#     print("Created file")

# การเขียนข้อมูล (Write data)
# with h5py.File('example.h5', 'w') as f:
#     data = np.arange(10)
#     f.create_dataset('my_data', data=data)

# สร้าง group:
# with h5py.File('example.h5', 'w') as f:
#     grp = f.create_group('my_group')
#     grp.create_dataset('data_in_group', data=np.arange(5))

# การอ่านข้อมูล (Read data)
# with h5py.File('example.h5', 'r') as f:
#     data = f['my_data'][:]   # อ่านทั้งหมด
#     # data = f['my_data'][0:5]  # อ่านบางส่วน
#     print(data)

# การอัพเดทข้อมูล (Update data) แก้ค่าใน dataset
# with h5py.File('example.h5', 'a') as f:
#     dset = f['my_data']
#     dset[0] = 999   # เปลี่ยนค่า index 0

# เพิ่ม dataset ใหม่
# with h5py.File('example.h5', 'a') as f:
#     f.create_dataset('new_data', data=[1,2,3])


# การลบข้อมูล (Delete data)
# with h5py.File('example.h5', 'a') as f:
#     del f['new_data']   # ลบ dataset


# ดูโครงสร้างทั้งหมด ──
# with h5py.File("example.h5", "r") as f:
#     f.visit(print)


import uuid

def generate_id():
    return str(uuid.uuid4())

print(generate_id())
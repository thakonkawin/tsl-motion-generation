
conda create -n sapiens2 python=3.12 -y
conda activate sapiens2

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

pip install -e .


hf download facebook/sapiens2-pose-1b sapiens2_1b_pose.safetensors
    --local-dir ~/sapiens2_host/pose

hf download facebook/detr-resnet-101-dc5 \
    --local-dir "/home/thakon/workspaces/sapiens2/sapiens2_host/detector/detr-resnet-101-dc5"


bash sapiens2/sapiens/pose/scripts/demo/keypoints308.sh


## Todo:
# Dead line 11-06-2026
- keypoint extracttion with sepains2 and manual remark point
- Fit smplx from keypoints


ข้าวผัด ฉัน กิน
กาแฟ ร้อน พ่อ ดื่ม
เสื้อผ้า แม่ ซัก
รูป การ์ตูน น้องสาว วาด
รถยนต์ พี่ชาย ขับ
ต้นไม้ ฉัน ปลูก
อาหาร อร่อย ยาย ทำ
ท้องฟ้า นก บิน
เด็กทารก ร้องไห้ เสียงดัง
โรงเรียน ฝนตก
ถนน น้ำ ท่วม
พรุ่งนี้ เที่ยว ฉัน ไป
วันนี้ อากาศ ร้อน มาก
เมื่อวาน ทำงาน พ่อ ไป ไม่
ฉัน ชอบ สีแดง

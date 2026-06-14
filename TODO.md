ข้อมูลของ keypoints ที่ได้จากในแต่ละเฟรมของวิดีโอ
tsl-motion-generation/test_keypoints/keypoints_data.json

code นี้เป็นส่งที่บอกว่า ตำแนห่งของแต่ละ joint ให้ตำแหน่งไหนบ้าง
tsl-motion-generation/sapiens2/sapiens/pose/configs/_base_/keypoints308.py

ในไฟล์
tsl-motion-generation/src/app/ui/preprocess_view.py
จะมี ui
keypoint_gallery = gr.Gallery(
                            label="Extracted Keypoints",
                            columns=8,
                            height=400,
                            interactive=True,
                            elem_id="#keypoint_gallery",
                        )
ให้คุณ custom css keypoint_gallery กดรูปภพไหนให้ popup หน้า editor สำหรับ edit pose เอาเฉพาะ pose, hands ไม่เอาหน้า
โดยที่ 
1. สามารถปรับเปลี่ยน zoom
2. ตำแหน่งของ แต่ละ joint แก้ไขได้อิสระจากการ ลาก mouse ที่จุด label ชื่อ joint โดยอิงจากข้อมูลรูปภาพ
3. จัดการกับรูปภาพที่เห็นครึ่งตัว ไม่้ห็นส่วนสะโพกลงไป เพราะว่า keypoint ได้ข้อมูลนี้ด้วย แต่ฉันจัด edit เอง
และมีปุ่ม OK ให้ update ข้อมูลใน keypoints_data.json ใหม่

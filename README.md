# 2FA OTP Manager

**2FA OTP Manager** เป็นแอปพลิเคชัน Python ที่ใช้จัดการ **Two-Factor Authentication (2FA)** สำหรับหลายบัญชี พร้อมสามารถ **สร้าง OTP**, **คัดลอก OTP**, และ **จัดการบัญชี** ได้อย่างสะดวก

---

## ฟีเจอร์หลัก

- เพิ่มบัญชีโดยระบุ **User/Email** และ **Secret Key**
- สร้าง OTP สำหรับบัญชีที่เลือก
- คัดลอก OTP ไปยัง Clipboard
- ลบบัญชีที่ไม่ต้องการ
- แสดงบัญชีทั้งหมดในรูปแบบ Scrollable List
- บันทึกบัญชีในไฟล์ `accounts.json` เพื่อเก็บข้อมูลข้ามการเปิดโปรแกรม
- ปรับ Layout ให้ใช้งานง่าย พร้อมปุ่ม Copy OTP ด้านล่าง Label
- ส่วน Credit แสดงผู้พัฒนา (DAPPER)

---

## วิธีติดตั้ง

1. ติดตั้ง Python 3.x (แนะนำ >= 3.10)
2. ติดตั้ง dependencies:

```bash
pip install pyotp

--

## วิธีเปิด

python 2fa_manager.py

--
# 2FA Manager (Web)

เว็บแอป 3 ชั้น (Frontend/Backend/DB) สำหรับจัดการ 2FA (TOTP) ด้วย Docker Compose

สถาปัตยกรรม
- Frontend: Nginx เสิร์ฟ static (HTML/JS/CSS)
- Backend: FastAPI + SQLAlchemy + pyotp + cryptography (Fernet)
- DB: PostgreSQL 16

ฟีเจอร์
- เพิ่ม/แก้ไข/ลบบัญชี: username, password, secret_key, note, digits, period
- สร้าง OTP (TOTP) และคัดลอกข้อมูลได้ผ่านปุ่มใน UI
- เข้ารหัส password/secret_key ในฐานข้อมูลด้วย Fernet key จาก `.env`

โครงสร้างโฟลเดอร์
- `backend/` โค้ด API (FastAPI)
- `frontend/` ไฟล์ static และ Nginx config
- `docker-compose.yml` รวมบริการ db/backend/frontend

วิธีรัน
1) เตรียม `.env` จากตัวอย่าง
```bash
cp .env.example .env
# สร้าง FERNET_KEY ด้วย Python:
# >>> python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
2) เริ่มระบบ
```bash
docker compose up -d
```
3) เปิดเว็บ (ค่าเริ่มต้น)
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000

ปรับพอร์ตผ่าน `.env`
- กำหนดพอร์ตฝั่งโฮสต์ได้ในไฟล์ `.env` (ดูตัวอย่างใน `env.example`)
  - `FRONTEND_PORT` (ดีฟอลต์ 8080)
  - `BACKEND_PORT`  (ดีฟอลต์ 8000)
  จากนั้น `docker compose up -d` จะผูกพอร์ตตามที่ตั้งไว้ และ UI จะเรียก API ผ่านเส้นทาง `/api` บนโดเมน/พอร์ตเดียวกัน

API หลัก (ย่อ)
- GET /api/accounts
- POST /api/accounts { username, password?, secret_key, note?, digits?, period? }
- PUT /api/accounts/{id}
- DELETE /api/accounts/{id}
- GET /api/accounts/{id}/otp
- GET /api/accounts/{id}/password
- GET /api/accounts/{id}/secret

ความปลอดภัย
- ต้องตั้ง `FERNET_KEY` คงที่ใน `.env` เพื่อถอดรหัสข้อมูลอ่อนไหวได้ในทุกครั้งที่รัน
- Backend เปิด CORS เฉพาะ origin ของ Frontend (แก้ได้ผ่าน `CORS_ORIGINS`)

ปิดโปรแกรม & ล้างแคช
- ปิดเฉพาะคอนเทนเนอร์ (คงสภาพข้อมูล): `docker compose stop`
- ปิดและลบคอนเทนเนอร์+เน็ตเวิร์ก (คงข้อมูลใน volume): `docker compose down`
- ปิดและลบพร้อมข้อมูลฐานข้อมูล (ล้าง volume): `docker compose down -v`
- ลบเฉพาะ volume ข้อมูล (ถ้าจำชื่อ): `docker volume rm 2FA_MANAGER_db_data`
- ล้างแคชการ build ของ Docker: `docker builder prune` (หรือทั้งหมด: `docker system prune -a` ระวังลบภาพ/แคชอื่นด้วย)
- ล้างแคชฝั่งเบราว์เซอร์ (กรณี UI ไม่อัปเดต): รีเฟรชแบบ hard (Ctrl/Cmd+Shift+R)

import tkinter as tk
import pyotp
import json
import os

DATA_FILE = "accounts.json"

accounts = {}       # เก็บข้อมูล {user: secret_key}
last_otps = {}      # เก็บ OTP ล่าสุดของแต่ละ user

# ---------- Persistence ----------
def load_accounts():
    global accounts
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            accounts = json.load(f)
    else:
        accounts = {}

def save_accounts():
    with open(DATA_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

# ---------- Functions ----------
def add_account():
    user = entry_user.get().strip()
    secret = entry_secret.get().strip()
    if user and secret:
        accounts[user] = secret
        save_accounts()
        refresh_accounts()
        entry_user.delete(0, tk.END)
        entry_secret.delete(0, tk.END)

def generate_otp(user):
    try:
        secret = accounts[user]
        totp = pyotp.TOTP(secret)
        otp = totp.now()
        last_otps[user] = otp  # เก็บค่า OTP ล่าสุด
        label_result.config(text=f"{user}\nOTP: {otp}", fg="green")
    except Exception as e:
        label_result.config(text=f"❌ Error: {e}", fg="red")

def copy_otp(user):
    if user in last_otps:
        otp = last_otps[user]
        root.clipboard_clear()
        root.clipboard_append(otp)
        root.update()
        label_result.config(text=f"{user}\nOTP: {otp} ✅ Copied!", fg="green")
    else:
        label_result.config(text="❌ ยังไม่มี OTP ให้ copy", fg="red")

def delete_account(user):
    if user in accounts:
        del accounts[user]
        if user in last_otps:
            del last_otps[user]
        save_accounts()
        refresh_accounts()
        label_result.config(text="")

def refresh_accounts():
    for widget in frame_accounts.winfo_children():
        widget.destroy()

    for user, secret in accounts.items():
        frame = tk.Frame(frame_accounts)
        frame.pack(fill="x", pady=2)

        lbl_user = tk.Label(frame, text=user, width=25, anchor="w")
        lbl_user.pack(side="left")

        lbl_secret = tk.Label(frame, text=secret, width=25, anchor="w", fg="gray")
        lbl_secret.pack(side="left")

        btn_gen = tk.Button(frame, text="Gen OTP", command=lambda u=user: generate_otp(u))
        btn_gen.pack(side="left", padx=5)

        btn_del = tk.Button(frame, text="Delete", command=lambda u=user: delete_account(u))
        btn_del.pack(side="left", padx=5)

def copy_current_otp():
    text = label_result.cget("text")  # ดึงข้อความจาก label_result
    if "OTP:" in text:
        otp_line = text.split("\n")[-1]  # เอาเฉพาะบรรทัด OTP
        otp = otp_line.replace("OTP: ", "").replace("✅ Copied!", "").strip()
        if otp:
            root.clipboard_clear()
            root.clipboard_append(otp)
            root.update()
            label_result.config(text=f"{text} ✅ Copied!")
            
# ---------------- UI ----------------
root = tk.Tk()
root.title("2FA OTP Manager")
root.geometry("750x500")  # ขยายสูงขึ้นเล็กน้อย

# Section: Header
label_header = tk.Label(root, text="2FA OTP MANAGER", font=("Arial", 28, "bold"), fg="white")
label_header.pack(pady=10)

# Section: Add account (user + secret)
# Frame รวมช่องกรอก
frame_add = tk.Frame(root)
frame_add.pack(pady=5)

# User
label_user = tk.Label(frame_add, text="User/Email:")
label_user.grid(row=0, column=0, padx=2, pady=2, sticky="e")  # ขวาแนบ Label
entry_user = tk.Entry(frame_add, width=20)
entry_user.grid(row=0, column=1, padx=2, pady=2)

# Secret Key
label_secret = tk.Label(frame_add, text="Secret Key:")
label_secret.grid(row=0, column=2, padx=10, pady=2, sticky="e")  # เว้นช่องว่าง
entry_secret = tk.Entry(frame_add, width=20)
entry_secret.grid(row=0, column=3, padx=2, pady=2)

# Confirm button
btn_add = tk.Button(frame_add, text="Confirm", command=add_account)
btn_add.grid(row=0, column=4, padx=10, pady=2)

# Section: Accounts list with scroll
frame_container = tk.Frame(root)
frame_container.pack(pady=10, fill="both", expand=True)

canvas = tk.Canvas(frame_container)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

frame_accounts = tk.Frame(canvas)
canvas.create_window((0,0), window=frame_accounts, anchor="nw")

# Section: Result (ใหญ่ขึ้น + สีเขียว)
frame_result = tk.Frame(root)
frame_result.pack(pady=10)

# Label OTP
label_result = tk.Label(frame_result, text="OTP: ", font=("Arial", 24, "bold"), fg="green")
label_result.pack(padx=5, pady=2)

# ปุ่ม Copy อยู่ด้านล่าง Label
btn_copy_result = tk.Button(frame_result, text="Copy OTP", command=copy_current_otp)
btn_copy_result.pack(padx=5, pady=2)

# Section: Credit มุมล่างขวา
label_credit = tk.Label(root, text="Edit by: DAPPER", font=("Arial", 10), fg="gray")
label_credit.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

# โหลด accounts ตอนเปิดโปรแกรม
load_accounts()
refresh_accounts()

root.mainloop()
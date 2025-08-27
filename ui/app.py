import tkinter as tk
from core.persistence import load_accounts, save_accounts
from core.otp_manager import generate_otp

accounts = {}
last_otps = {}

def add_account(entry_user, entry_secret, refresh_accounts):
    user = entry_user.get().strip()
    secret = entry_secret.get().strip()
    if user and secret:
        accounts[user] = secret
        save_accounts(accounts)
        refresh_accounts()
        entry_user.delete(0, tk.END)
        entry_secret.delete(0, tk.END)

def generate_otp_ui(user, label_result):
    try:
        secret = accounts[user]
        otp = generate_otp(secret)
        last_otps[user] = otp
        label_result.config(text=f"{user}\nOTP: {otp}", fg="green")
    except Exception as e:
        label_result.config(text=f"❌ Error: {e}", fg="red")

def copy_otp(user, root, label_result):
    if user in last_otps:
        otp = last_otps[user]
        root.clipboard_clear()
        root.clipboard_append(otp)
        root.update()
        label_result.config(text=f"{user}\nOTP: {otp} ✅ Copied!", fg="green")
    else:
        label_result.config(text="❌ ยังไม่มี OTP ให้ copy", fg="red")

def delete_account(user, refresh_accounts, label_result):
    if user in accounts:
        del accounts[user]
        if user in last_otps:
            del last_otps[user]
        save_accounts(accounts)
        refresh_accounts()
        label_result.config(text="")

def refresh_accounts(frame_accounts, label_result, root):
    for widget in frame_accounts.winfo_children():
        widget.destroy()
    for user, secret in accounts.items():
        frame = tk.Frame(frame_accounts)
        frame.pack(fill="x", pady=2)
        lbl_user = tk.Label(frame, text=user, width=25, anchor="w")
        lbl_user.pack(side="left")
        lbl_secret = tk.Label(frame, text=secret, width=25, anchor="w", fg="gray")
        lbl_secret.pack(side="left")
        btn_gen = tk.Button(frame, text="Gen OTP", command=lambda u=user: generate_otp_ui(u, label_result))
        btn_gen.pack(side="left", padx=5)
        btn_del = tk.Button(frame, text="Delete", command=lambda u=user: delete_account(u, lambda: refresh_accounts(frame_accounts, label_result, root), label_result))
        btn_del.pack(side="left", padx=5)

def copy_current_otp(label_result, root):
    text = label_result.cget("text")
    if "OTP:" in text:
        otp_line = text.split("\n")[-1]
        otp = otp_line.replace("OTP: ", "").replace("✅ Copied!", "").strip()
        if otp:
            root.clipboard_clear()
            root.clipboard_append(otp)
            root.update()
            label_result.config(text=f"{text} ✅ Copied!")

def run_app():
    global accounts
    root = tk.Tk()
    root.title("2FA OTP Manager")
    root.geometry("750x500")

    label_header = tk.Label(root, text="2FA OTP MANAGER", font=("Arial", 28, "bold"), fg="white")
    label_header.pack(pady=10)

    frame_add = tk.Frame(root)
    frame_add.pack(pady=5)
    label_user = tk.Label(frame_add, text="User/Email:")
    label_user.grid(row=0, column=0, padx=2, pady=2, sticky="e")
    entry_user = tk.Entry(frame_add, width=20)
    entry_user.grid(row=0, column=1, padx=2, pady=2)
    label_secret = tk.Label(frame_add, text="Secret Key:")
    label_secret.grid(row=0, column=2, padx=10, pady=2, sticky="e")
    entry_secret = tk.Entry(frame_add, width=20)
    entry_secret.grid(row=0, column=3, padx=2, pady=2)
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
    frame_result = tk.Frame(root)
    frame_result.pack(pady=10)
    label_result = tk.Label(frame_result, text="OTP: ", font=("Arial", 24, "bold"), fg="green")
    label_result.pack(padx=5, pady=2)
    btn_copy_result = tk.Button(frame_result, text="Copy OTP", command=lambda: copy_current_otp(label_result, root))
    btn_copy_result.pack(padx=5, pady=2)
    label_credit = tk.Label(root, text="Edit by: DAPPER", font=("Arial", 10), fg="gray")
    label_credit.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    def refresh():
        refresh_accounts(frame_accounts, label_result, root)

    btn_add = tk.Button(frame_add, text="Confirm", command=lambda: add_account(entry_user, entry_secret, refresh))
    btn_add.grid(row=0, column=4, padx=10, pady=2)

    accounts = load_accounts()
    refresh()

    root.mainloop()

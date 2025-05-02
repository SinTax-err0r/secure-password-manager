import tkinter as tk
from tkinter import simpledialog, messagebox, Scrollbar
import json
import os
import hashlib
from cryptography.fernet import Fernet

MASTER_HASH_FILE = "master.hash"
DATA_FILE = "vault.json"
KEY_FILE = "secret.key"

# ---------- Encryption Utilities ----------

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(data, key):
    f = Fernet(key)
    return f.decrypt(data).decode()

# ---------- Master Password ----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_master_password():
    if not os.path.exists(MASTER_HASH_FILE):
        pwd = simpledialog.askstring("Set Master Password", "Create a master password:", show="*")
        if not pwd:
            quit()
        with open(MASTER_HASH_FILE, "w") as f:
            f.write(hash_password(pwd))
        messagebox.showinfo("Success", "Master password set successfully.")
        return pwd
    else:
        with open(MASTER_HASH_FILE, "r") as f:
            stored_hash = f.read().strip()

        for attempt in range(5):
            pwd = simpledialog.askstring("Enter Master Password", f"Attempt {attempt + 1}/5: Enter your master password:", show="*")
            if not pwd:
                quit()
            if hash_password(pwd) == stored_hash:
                return pwd
            else:
                messagebox.showerror("Error", "Incorrect master password.")
        messagebox.showerror("Access Denied", "Too many incorrect attempts. Exiting.")
        quit()

# ---------- Storage ----------

def save_data(data, key):
    enc = encrypt_data(json.dumps(data), key)
    with open(DATA_FILE, "wb") as f:
        f.write(enc)

def load_data(key):
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "rb") as f:
        enc = f.read()
        return json.loads(decrypt_data(enc, key))

# ---------- UI ----------

class PasswordManagerApp:
    def __init__(self, master_pwd):
        self.master_pwd = master_pwd
        self.key = load_key()
        self.data = load_data(self.key)

        self.root = tk.Tk()
        self.root.title("Secure Password Manager")
        self.root.geometry("500x500")

        self.is_dark_mode = False

        # Toggle dark mode
        self.toggle_button = tk.Button(self.root, text="🌙", command=self.toggle_theme)
        self.toggle_button.pack(anchor="ne", padx=5, pady=5)

        tk.Label(self.root, text="Keyword").pack()
        self.keyword_entry = tk.Entry(self.root, width=40)
        self.keyword_entry.pack(pady=5)

        tk.Label(self.root, text="Password").pack()
        self.password_entry = tk.Entry(self.root, width=40, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Add Password", command=self.add_password).pack(pady=5)
        tk.Button(self.root, text="Clear Inputs", command=self.clear_inputs).pack()

        # Scrollable keyword list
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True, pady=10)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self.frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar.config(command=self.canvas.yview)

        self.list_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.load_keywords()

        self.root.mainloop()

    def toggle_theme(self):
    self.is_dark_mode = not self.is_dark_mode
    bg = "#2c2c2c" if self.is_dark_mode else "#f0f0f0"
    fg = "#ffffff" if self.is_dark_mode else "#000000"

    self.root.configure(bg=bg)
    self.canvas.configure(bg=bg)
    self.list_frame.configure(bg=bg)
    self.frame.configure(bg=bg)

    for widget in self.root.winfo_children():
        try:
            widget.configure(bg=bg, fg=fg)
        except:
            pass

    for widget in self.frame.winfo_children():
        try:
            widget.configure(bg=bg, fg=fg)
        except:
            pass

    for widget in self.list_frame.winfo_children():
        try:
            widget.configure(bg=bg)
            for sub in widget.winfo_children():
                sub.configure(bg=bg, fg=fg)
        except:
            pass


    def add_password(self):
        k = self.keyword_entry.get()
        p = self.password_entry.get()

        if not k or not p:
            messagebox.showwarning("Warning", "Please enter both keyword and password.")
            return

        self.data[k] = p
        save_data(self.data, self.key)
        self.load_keywords()
        self.clear_inputs()

    def clear_inputs(self):
        self.keyword_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def load_keywords(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for keyword in sorted(self.data.keys()):
            frame = tk.Frame(self.list_frame)
            frame.pack(pady=2, fill="x")

            tk.Label(frame, text=keyword, width=25, anchor="w").pack(side="left", padx=5)

            tk.Button(frame, text="View", command=lambda k=keyword: self.view_password(k)).pack(side="right", padx=2)
            tk.Button(frame, text="Delete", command=lambda k=keyword: self.delete_password(k)).pack(side="right", padx=2)

    def view_password(self, keyword):
        attempt = simpledialog.askstring("Authenticate", "Enter master password:", show="*")
        if not attempt:
            return
        if hash_password(attempt) == hash_password(self.master_pwd):
            messagebox.showinfo(f"Password for {keyword}", self.data[keyword])
        else:
            messagebox.showerror("Error", "Incorrect master password.")

    def delete_password(self, keyword):
        attempt = simpledialog.askstring("Authenticate", "Enter master password to delete:", show="*")
        if not attempt:
            return
        if hash_password(attempt) == hash_password(self.master_pwd):
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the password for '{keyword}'?")
            if confirm:
                del self.data[keyword]
                save_data(self.data, self.key)
                self.load_keywords()
        else:
            messagebox.showerror("Error", "Incorrect master password.")

# ---------- Main Execution ----------

if __name__ == "__main__":
    if not os.path.exists(KEY_FILE):
        generate_key()

    master_password = verify_master_password()
    PasswordManagerApp(master_password)

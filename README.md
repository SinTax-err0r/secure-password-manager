# 🔐 Secure Password Manager

A simple yet secure password manager built with **Python** and **Tkinter**.  
Designed for offline use, it encrypts your saved passwords and requires a **master password** for access.

---

## 🚀 Features

- **Master Password Authentication** (stored as a secure SHA-256 hash)
- **AES Encryption** of saved passwords using the `cryptography` library
- **Add and View Passwords** tied to custom keywords
- **Password Visibility Control** – master password required before viewing
- **Scrollable UI** for managing many saved entries
- **Dark Mode Toggle** ☀️🌙
- **Limited Login Attempts** – closes after 5 incorrect master password attempts

---

## 🖼️ UI Preview

> Insert a screenshot here if you like  
> (You can take a screenshot of the app and drag it into the README section of GitHub after uploading)

---

## 🧠 How It Works

1. On first run, you'll be asked to **create a master password**.
2. A **secret key** (`secret.key`) is generated for encrypting/decrypting your data.
3. Passwords are stored securely in `vault.json` after encryption.
4. You can **add passwords** tied to keywords (e.g., `gmail`, `netflix`).
5. To **view a saved password**, the master password must be entered again.

---

## 📦 Files Explained

| File            | Purpose                                                   |
|-----------------|-----------------------------------------------------------|
| `main.py`       | Main application code                                     |
| `master.hash`   | Stores the hashed master password                         |
| `secret.key`    | AES key used for encryption                               |
| `vault.json`    | Encrypted storage of user passwords                       |

---

## ⚙️ Requirements

- Python 3.x
- `cryptography` library

Install it with:

```bash
pip install cryptography

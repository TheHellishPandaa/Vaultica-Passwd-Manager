# -*- coding: utf-8 -*-
# Vaultica Password Manager for Linux, Windows & MacOS
# Author: Jaime Galvez Martinez
# Version: 1.0.1
# DATE: 20/07/2025
# Original Project: December 2024 as GNU-PasswdManager
# LICENSE: GNU (General Public License)

# -------- Import Libraries -------- #
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from cryptography.fernet import Fernet
import json
import os
import sys
import random
import string
import bcrypt

# --- Globals ---
key = None
users = {}
dark_mode = True

# --- Key Management ---
def generate_key():
    return Fernet.generate_key()

def load_key(filename='key.key'):
    if not os.path.exists(filename):
        with open(filename, 'wb') as file:
            file.write(generate_key())
    with open(filename, 'rb') as file:
        return file.read()

# --- Data Handling ---
def load_data(filename='users.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

def save_data(data, filename='users.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def setup_users_file(filename='users.json'):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump({}, file, indent=4)
        try:
            os.chmod(filename, 0o600)
            if hasattr(os, 'chown'):
                os.chown(filename, 0, 0)
        except:
            pass

def ensure_superuser():
    if os.name != "nt" and os.geteuid() != 0:
        print("Este script debe ejecutarse con privilegios de superusuario (sudo).")
        sys.exit(1)

# --- Theming ---
def get_theme_colors():
    return ("#121212", "#f0f0f0") if dark_mode else ("#f0f0f0", "#000000")

def apply_theme(widget, bg, fg):
    widget.configure(bg=bg)
    for child in widget.winfo_children():
        if isinstance(child, (tk.Frame, tk.LabelFrame)):
            apply_theme(child, bg, fg)
        else:
            try:
                child.configure(bg=bg, fg=fg)
            except:
                pass

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme(root, *get_theme_colors())

# --- Password Management ---
def generate_password(user):
    length = simpledialog.askinteger("Generar Contraseña", "Longitud (14-64):", minvalue=14, maxvalue=64)
    if not length:
        return
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    service = simpledialog.askstring("Servicio", "Nombre del Servicio:")
    service_user = simpledialog.askstring("Usuario", "Nombre del Usuario del Servicio:")
    if not service:
        return
    passwords = load_passwords(user)
    fernet = Fernet(key)
    uid = str(len(passwords) + 1)
    passwords[uid] = {
        'service': service,
        'username': service_user,
        'password': fernet.encrypt(password.encode()).decode()
    }
    save_passwords(user, passwords)
    messagebox.showinfo("Generado", f"Contraseña Guardada con éxito.")

def load_passwords(user, filename='passwords.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            return data.get(user, {})
    return {}

def save_passwords(user, passwords, filename='passwords.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
    else:
        data = {}
    data[user] = passwords
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def add_password(user):
    service = simpledialog.askstring("Servicio", "Nombre del Servicio:")
    service_user = simpledialog.askstring("Usuario", "Nombre de Usuario del Servicio:")
    password = simpledialog.askstring("Contraseña", "Contraseña:", show='*')
    if not (service and service_user and password):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    passwords = load_passwords(user)
    uid = str(len(passwords) + 1)
    fernet = Fernet(key)
    passwords[uid] = {
        'service': service,
        'username': service_user,
        'password': fernet.encrypt(password.encode()).decode()
    }
    save_passwords(user, passwords)
    messagebox.showinfo("Éxito", f"Contraseña guardada con ID {uid}.")

# ----------- Show Password ----------- #
def show_passwords(user):
    passwords = load_passwords(user)
    if not passwords:
        messagebox.showinfo("Vacío", "No tienes contraseñas guardadas.")
        return

    fernet = Fernet(key)

    window = tk.Toplevel(root)
    window.title("Contraseñas Guardadas")
    window.geometry("600x400")
    bg, fg = get_theme_colors()
    window.configure(bg=bg)

    tree = ttk.Treeview(window, columns=("ID", "Servicio", "Usuario", "Contraseña"), show='headings')
    for col in ("ID", "Servicio", "Usuario", "Contraseña"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(expand=True, fill='both')

    for uid, entry in passwords.items():
        pw_masked = "********"
        tree.insert("", tk.END, values=(uid, entry['service'], entry['username'], pw_masked))

    show_var = tk.BooleanVar()

    def toggle_view():
        for item in tree.get_children():
            values = tree.item(item, 'values')
            pw_plain = fernet.decrypt(passwords[values[0]]['password'].encode()).decode()
            tree.item(item, values=(values[0], values[1], values[2], pw_plain if show_var.get() else "********"))

    def copy_password():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona una contraseña.")
            return

        uid = str(tree.item(selected[0], 'values')[0])
        if uid not in passwords:
            messagebox.showerror("Error", "No se encontró la contraseña.")
            return

        try:
            encrypted_pw = passwords[uid]['password']
            decrypted_pw = fernet.decrypt(encrypted_pw.encode()).decode()
            window.clipboard_clear()
            window.clipboard_append(decrypted_pw)
            window.update()
            messagebox.showinfo("Copiada", "Contraseña copiada al portapapeles.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar la contraseña.\n{e}")

    toggle_btn = tk.Checkbutton(window, text="Mostrar Contraseñas", variable=show_var, command=toggle_view)
    toggle_btn.pack(pady=5)

    copy_btn = tk.Button(window, text="Copiar Contraseña Seleccionada", command=copy_password)
    copy_btn.pack(pady=5)

    apply_theme(window, bg, fg)


# --- Authentication ---
def register_user():
    user = simpledialog.askstring("Registro", "Nombre de usuario:")
    if not user or user in users:
        messagebox.showerror("Error", "Nombre inválido o ya existe.")
        return
    password = simpledialog.askstring("Registro", "Contraseña:", show='*')
    if not password:
        return
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[user] = {'password': hashed}
    save_data(users)
    messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente.")

def login_user():
    user = simpledialog.askstring("Login", "Nombre de usuario:")
    if user not in users:
        messagebox.showerror("Error", "Usuario no encontrado.")
        return None
    password = simpledialog.askstring("Login", "Contraseña:", show='*')
    hashed = users[user]['password'].encode()
    if bcrypt.checkpw(password.encode(), hashed):
        return user
    else:
        messagebox.showerror("Error", "Contraseña incorrecta.")
        return None

# --- GUI Setup ---
ensure_superuser()
setup_users_file()
key = load_key()
users = load_data()

root = tk.Tk()
root.title("Vaultica PassworddManager")
root.geometry("1200x800")
root.configure(bg=get_theme_colors()[0])

def open_login():
    user = login_user()
    if user:
        login_frame.pack_forget()
        show_panel(user)

def show_panel(user):
    panel_frame = tk.Frame(root, bg=get_theme_colors()[0])
    panel_frame.pack(pady=20)

    title = tk.Label(panel_frame, text="Vaultica-PasswordManager", font=("Arial Black", 42, "bold"))
    title.pack(pady=10)

    tk.Button(panel_frame, text="Añadir Contraseña", command=lambda: add_password(user), width=30).pack(pady=5)
    tk.Button(panel_frame, text="Generar Contraseña", command=lambda: generate_password(user), width=30).pack(pady=5)
    tk.Button(panel_frame, text="Mostrar Contraseñas", command=lambda: show_passwords(user), width=30).pack(pady=5)
    tk.Button(panel_frame, text="Activar/Desactivar Modo Oscuro", command=toggle_dark_mode, width=30).pack(pady=5)
    tk.Button(panel_frame, text="Cerrar sesión/Salir del Programa", command=root.quit, width=30).pack(pady=5)

    apply_theme(panel_frame, *get_theme_colors())

login_frame = tk.Frame(root, bg=get_theme_colors()[0])
login_frame.pack(pady=20)

login_btn = tk.Button(login_frame, text="Iniciar Sesión", command=open_login, width=26)
login_btn.pack(pady=5)
register_btn = tk.Button(login_frame, text="Registrar Usuario", command=register_user, width=26)
register_btn.pack(pady=5)

apply_theme(login_frame, *get_theme_colors())

root.mainloop()


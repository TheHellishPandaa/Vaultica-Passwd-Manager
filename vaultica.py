# AUTHOR: JAIME GALVEZ MARTINEZ
# DATE: 19/07/2025
# VERSION: 1.0
# Vaultica Password Manager 

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from cryptography.fernet import Fernet
import json
import os
import sys
import random
import string

# --- CONFIGURACIÓN DE MODO OSCURO ---
dark_mode = True  # Iniciar con modo oscuro activado

def get_theme_colors():
    return ("#121212", "white") if dark_mode else ("#f0f0f0", "black")

def apply_theme(widget, bg_color, fg_color):
    try:
        widget.configure(bg=bg_color, fg=fg_color)
    except:
        try:
            widget.configure(bg=bg_color)
        except:
            pass
    for child in widget.winfo_children():
        apply_theme(child, bg_color, fg_color)

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    bg_color, fg_color = get_theme_colors()
    root.configure(bg=bg_color)
    apply_theme(root, bg_color, fg_color)

# --- FUNCIONES DE ENCRIPTADO ---
def generate_key():
    return Fernet.generate_key()

def load_key(filename='key.key'):
    if not os.path.exists(filename):
        key = generate_key()
        with open(filename, 'wb') as file:
            file.write(key)
    else:
        with open(filename, 'rb') as file:
            key = file.read()
    return key

# --- ARCHIVO DE USUARIOS ---
def load_data(filename='users.json'):
    return json.load(open(filename)) if os.path.exists(filename) else {}

def save_data(data, filename='users.json'):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def setup_users_file(filename='users.json'):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump({}, file, indent=4)
        os.chmod(filename, 0o600)
        try:
            os.chown(filename, 0, 0)
        except AttributeError:
            pass

def ensure_superuser():
    if os.name != "nt" and os.geteuid() != 0:
        print("Ejecuta este script con permisos de superusuario.")
        sys.exit(1)

# --- CONTRASEÑAS ---
def load_passwords(user, filename='passwords.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            if user in data:
                return data[user]
    return {}

def save_passwords(user, passwords, filename='passwords.json'):
    data = {}
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
    data[user] = passwords
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def generate_password(user):
    length = simpledialog.askinteger("Generar Contraseña", "Longitud (8-32):", minvalue=8, maxvalue=32)
    if length:
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
        service = simpledialog.askstring("Servicio", "¿Para qué servicio es?")
        if service:
            passwords = load_passwords(user)
            fernet = Fernet(key)
            unique_id = str(len(passwords) + 1)
            passwords[unique_id] = {
                'service': service,
                'username': 'Generado',
                'password': fernet.encrypt(password.encode()).decode()
            }
            save_passwords(user, passwords)
            messagebox.showinfo("Contraseña Generada", f"{password} (guardada automáticamente)")
        else:
            messagebox.showerror("Error", "Servicio requerido.")
    else:
        messagebox.showerror("Error", "Longitud inválida.")

def add_password(user):
    service = simpledialog.askstring("Servicio", "Nombre del servicio:")
    username = simpledialog.askstring("Usuario", "Nombre de usuario:")
    password = simpledialog.askstring("Contraseña", "Introduce la contraseña:", show="*")
    if service and username and password:
        passwords = load_passwords(user)
        fernet = Fernet(key)
        unique_id = str(len(passwords) + 1)
        passwords[unique_id] = {
            'service': service,
            'username': username,
            'password': fernet.encrypt(password.encode()).decode()
        }
        save_passwords(user, passwords)
        messagebox.showinfo("Guardado", f"Contraseña guardada con ID: {unique_id}")
    else:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")

def show_passwords(user):
    passwords = load_passwords(user)
    if not passwords:
        messagebox.showinfo("Sin Contraseñas", "No hay contraseñas guardadas.")
        return

    def copy_to_clipboard():
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Selecciona una contraseña.")
            return
        values = tree.item(selected, "values")
        password = values[3]
        root.clipboard_clear()
        root.clipboard_append(password)
        root.update()
        messagebox.showinfo("Copiado", "Contraseña copiada al portapapeles.")

    def toggle_show_password():
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Selecciona una fila.")
            return
        item = tree.item(selected)
        values = list(item["values"])
        real_id = values[0]
        if values[3] == "********":
            values[3] = Fernet(key).decrypt(passwords[real_id]['password'].encode()).decode()
        else:
            values[3] = "********"
        tree.item(selected, values=values)

    show_window = tk.Toplevel(root)
    show_window.title("Contraseñas Guardadas")
    show_window.geometry("700x500")
    bg_color, fg_color = get_theme_colors()
    show_window.configure(bg=bg_color)

    tree = ttk.Treeview(show_window, columns=("ID", "Servicio", "Usuario", "Contraseña"), show='headings')
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill="both")

    fernet = Fernet(key)
    for uid, data in passwords.items():
        tree.insert("", tk.END, values=(uid, data['service'], data['username'], "********"))

    btns = tk.Frame(show_window, bg=bg_color)
    tk.Button(btns, text="Copiar", command=copy_to_clipboard).pack(side="left", padx=5, pady=10)
    tk.Button(btns, text="Mostrar/Ocultar", command=toggle_show_password).pack(side="left", padx=5)
    btns.pack()

    apply_theme(show_window, bg_color, fg_color)

# --- AUTENTICACIÓN ---
def register_user():
    user = simpledialog.askstring("Registro", "Nombre de usuario:")
    if user in users:
        messagebox.showerror("Error", "Usuario ya existe.")
        return
    password = simpledialog.askstring("Registro", "Contraseña:", show="*")
    if user and password:
        users[user] = {'password': password}
        save_data(users)
        messagebox.showinfo("Éxito", "Usuario registrado.")
    else:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")

def login_user():
    user = simpledialog.askstring("Login", "Nombre de usuario:")
    if user not in users:
        messagebox.showerror("Error", "Usuario no encontrado.")
        return None
    password = simpledialog.askstring("Login", "Contraseña:", show="*")
    if users[user]['password'] == password:
        return user
    else:
        messagebox.showerror("Error", "Contraseña incorrecta.")
      return None
      
# --- GUI ---
ensure_superuser()
setup_users_file()
key = load_key()
users = load_data()

# Estado inicial del tema
dark_mode = True  # Si quieres que empiece en modo oscuro
bg_color, fg_color = get_theme_colors()

# Crear ventana principal
root = tk.Tk()
root.title("Vaultica")
root.geometry("1200x800")
root.configure(bg=bg_color)

# Función para cambiar a la vista principal después de login
def open_login():
    user = login_user()
    if user:
        login_frame.pack_forget()
        show_panel(user)

# Función principal del panel tras login
def show_panel(user):
    panel_frame = tk.Frame(root, bg=bg_color)
    panel_frame.pack(pady=20)

    title = tk.Label(panel_frame, text="Vaultica-PasswdManager", font=("Arial Black", 36, "bold"))
    title.pack(pady=10)

    tk.Button(panel_frame, text="Añadir Contraseña", command=lambda: add_password(user), width=25).pack(pady=5)
    tk.Button(panel_frame, text="Generar Contraseña", command=lambda: generate_password(user), width=25).pack(pady=5)
    tk.Button(panel_frame, text="Mostrar Contraseñas", command=lambda: show_passwords(user), width=25).pack(pady=5)
    tk.Button(panel_frame, text="🌙 Modo Oscuro", command=toggle_dark_mode, width=25).pack(pady=5)
    tk.Button(panel_frame, text="Cerrar sesión", command=root.quit, width=25).pack(pady=5)

    apply_theme(panel_frame, *get_theme_colors())

# --- Login Frame ---
login_frame = tk.Frame(root, bg=bg_color)
login_frame.pack(pady=20)

login_btn = tk.Button(login_frame, text="Iniciar Sesión", command=open_login, width=25)
login_btn.pack(pady=5)

register_btn = tk.Button(login_frame, text="Registrar Usuario", command=register_user, width=25)
register_btn.pack(pady=5)

apply_theme(login_frame, *get_theme_colors())

# --- Ejecutar interfaz ---
root.mainloop()

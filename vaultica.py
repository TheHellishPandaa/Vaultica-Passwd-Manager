# -*- coding: utf-8 -*-
# Vaultica Password Manager for Linux, Windows & MacOS
# Author: Jaime Galvez Martinez
# Version: 1.0.2
# DATE: 21/07/2025
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
import re

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
        print("Este programa debe ejecutarse con privilegios de superusuario (sudo).")
        sys.exit(1)

# --- Theming ---
def get_theme_colors():
    return ("#121213", "#f0f0f0") if dark_mode else ("#f0f0f0", "#000000")

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
    length = simpledialog.askinteger("Generar Contraseña", "Longitud (14-128):", minvalue=14, maxvalue=128)
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
    service = simpledialog.askstring("Servicio", "Nombre del Servicio:*")
    service_user = simpledialog.askstring("Usuario", "Nombre del Usuario del Servicio:*")
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


# --- Testing Valid Password ---#

def is_valid_password(pwd):
    return (
        len(pwd) >= 8 and
        any(c.islower() for c in pwd) and
        any(c.isupper() for c in pwd)
    )

# --- Autentication --- #
def register_user():
    user = simpledialog.askstring("Registro - La contraseña debe tener al menos 8 caracteres, una letra mayúscula y una minúscula","Nombre de usuario:")
    if not user or user in users:
        messagebox.showerror("Error", "Nombre inválido o ya existe.")
        return

    password1 = simpledialog.askstring("Registro ", "Contraseña:", show='*')
    if not password1:
        return

    password2 = simpledialog.askstring("Registro", "Repite la Contraseña:", show='*')
    if password2 != password1:
        messagebox.showerror("Error", "La segunda contraseña no coincide.")
        return

    password3 = simpledialog.askstring("Registro", "Confirma la Contraseña por tercera vez:", show='*')
    if password3 != password1:
        messagebox.showerror("Error", "La tercera contraseña no coincide.")
        return

    if not is_valid_password(password1):
        messagebox.showerror(
            "Error de seguridad",
            "La contraseña debe tener al menos 8 caracteres, una letra mayúscula y una minúscula."
        )
        return

    # We force the configuration of security questions (required)
    security_questions = get_security_questions()
    if not security_questions:
        messagebox.showerror("Error", "Debes completar todas las preguntas de seguridad para registrarte.")
        return

    hashed = bcrypt.hashpw(password1.encode(), bcrypt.gensalt()).decode()
    users[user] = {
        'password': hashed,
        'security': security_questions
    }
    save_data(users)
    messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente.")

def get_security_questions():
    fixed_questions = [
        "1/4 ¿En qué ciudad naciste?*",
        "2/4 ¿Cuál es tu grupo de música favorito?*",
        "3/4 ¿En qué pueblo / ciudad vivías a los 10 años?*",
        "4/4 ¿Qué tipo de mascota tuviste primero (perro, gato, etc.)*?"
    ]
    
    security_questions = []
    respuestas_usadas = set()

# ------- check security questions --------
    for question in fixed_questions:
        while True:
            answer1 = simpledialog.askstring("Pregunta de seguridad (obligatorio)", f"{question} (Primera vez)", show='*')
            if answer1 is None:
                return None
            answer2 = simpledialog.askstring("Pregunta de seguridad (obligatorio)", f"{question} (Confirma respuesta)", show='*')
            if answer2 is None:
                return None

            answer1 = answer1.strip()
            answer2 = answer2.strip()

            if answer1 != answer2:
                messagebox.showerror("Error", "Las respuestas no coinciden. Intenta de nuevo.")
                continue

            if not answer1:
                messagebox.showerror("Error", "La respuesta no puede estar vacía.")
                continue

            normalized = answer1.lower()
            if normalized in respuestas_usadas:
                messagebox.showerror("Error", "Esta respuesta ya fue utilizada en otra pregunta. Debe ser diferente.")
                continue

            respuestas_usadas.add(normalized)
            hashed_answer = bcrypt.hashpw(answer1.encode(), bcrypt.gensalt()).decode()
            security_questions.append({
                'question': question,
                'answer': hashed_answer
            })
            break

    return security_questions

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

def reset_password():
    user = simpledialog.askstring("Recuperar Contraseña", "Nombre de usuario:")
    if not user or user not in users:
        messagebox.showerror("Error", "Usuario no encontrado.")
        return

    # ------ Check if the user has security questions configured -------- #
    if "security" not in users[user] or not users[user]["security"]:
        response = messagebox.askyesno(
            "Preguntas de seguridad no configuradas",
            "Este usuario no tiene configuradas preguntas de seguridad.\n¿Deseas configurarlas ahora?"
        )
        if not response:
            return

        
        new_security = get_security_questions()
        if not new_security:
            return  
        users[user]["security"] = new_security
        save_data(users)
        messagebox.showinfo("Listo", "Preguntas de seguridad guardadas correctamente.\nPuedes intentar recuperar la contraseña ahora.")
        return 

    # ------ Validate questions --------
    questions = users[user]["security"]
    for qa in questions:
        answer = simpledialog.askstring("Pregunta de Seguridad", qa['question'], show='*')
        if not answer or not bcrypt.checkpw(answer.encode(), qa['answer'].encode()):
            messagebox.showerror("Error", "Respuesta incorrecta.")
            return

    # Change Password ------
    new_password = simpledialog.askstring("Nueva Contraseña", "Introduce la nueva contraseña:", show='*')
    if not new_password:
        return
    confirm_password = simpledialog.askstring("Confirma Contraseña", "Vuelve a introducir la nueva contraseña:", show='*')

    if new_password != confirm_password:
        messagebox.showerror("Error", "Las contraseñas no coinciden.")
        return
    if not is_valid_password(new_password):
        messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres, una letra mayúscula y una letra minúscula.")
        return

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    users[user]['password'] = hashed
    save_data(users)
    messagebox.showinfo("Éxito", "La contraseña fue restablecida correctamente.")


# --- GUI Setup ---
ensure_superuser()
setup_users_file()
key = load_key()
users = load_data()

root = tk.Tk()
root.title("Vaultica Password Manager")
root.geometry("1600x900")
root.configure(bg=get_theme_colors()[0])

def open_login():
    user = login_user()
    if user:
        login_frame.pack_forget()
        show_panel(user)

def show_panel(user):
    panel_frame = tk.Frame(root, bg=get_theme_colors()[0])
    panel_frame.pack(pady=20)

    title = tk.Label(panel_frame, text="Vaultica Password Manager", font=("Arial Black", 42, "bold"))
    title.pack(pady=10)

    tk.Button(panel_frame, text="Añadir Contraseña", command=lambda: add_password(user), width=30).pack(pady=5)
    tk.Button(panel_frame, text="Generar Contraseña", command=lambda: generate_password(user), width=30).pack(pady=5)
    tk.Button(panel_frame, text="Mostrar Contraseñas", command=lambda: show_passwords(user), width=30).pack(pady=5)
    tk.Button(panel_frame, text="Activar/Desactivar Modo Oscuro", command=toggle_dark_mode, width=30).pack(pady=5)
    tk.Button(panel_frame, text="Cerrar sesión/Salir del Programa", command=root.quit, width=30).pack(pady=5)

    apply_theme(panel_frame, *get_theme_colors())

login_frame = tk.Frame(root, bg=get_theme_colors()[0])
login_frame.pack(pady=20)


# ------ login panel ---------#
login_btn = tk.Button(login_frame, text="Iniciar Sesión", command=open_login, width=32)
login_btn.pack(pady=7)

register_btn = tk.Button(login_frame, text="Registrar Usuario", command=register_user, width=32)
register_btn.pack(pady=7)

recover_btn = tk.Button(login_frame, text="¿Olvidaste tu contraseña?", command=reset_password, width=32)
recover_btn.pack(pady=7)

tk.Button(login_frame, text="Salir del Programa", command=root.quit, width=32).pack(pady=7)

tk.Button(login_frame, text="Activar/Desactivar Modo Oscuro", command=toggle_dark_mode, width=32).pack(pady=7)

apply_theme(login_frame, *get_theme_colors())

root.mainloop()

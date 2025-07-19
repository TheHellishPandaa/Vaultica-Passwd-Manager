# Vaultica-Passwd-Manager
# 🔐 Vaultica Password Manager

**Vaultica** es un gestor de contraseñas seguro y de código abierto, escrito en Python con interfaz gráfica (`Tkinter`) y cifrado avanzado con `cryptography.Fernet`.

Diseñado para usuarios que valoran la seguridad, la simplicidad y el control total sobre sus datos.

---

## 📦 Características

- 🧩 Interfaz gráfica simple y funcional
- 🔐 Cifrado de contraseñas con claves Fernet
- 🔑 Generación de contraseñas aleatorias seguras
- 👤 Gestión de múltiples usuarios
- 🧾 Visualización y copia rápida de contraseñas
- 🛡️ Requiere permisos de superusuario en Linux para mayor seguridad
- 🇪🇸 Interfaz completamente en español

---

## 🖥️ Requisitos

- Python 3.8 o superior
- pip
- Linux o Windows (mejor en Linux para funciones `sudo`)
- Módulos Python:
  - `cryptography`
  - `tkinter` (en Linux: `python3-tk`)

---

## 🚀 Instalación

1. **Clona el repositorio:**
   ```
   git clone https://github.com/TheHellishPandaa/vaultica.git
   cd vaultica
   ```

### ▶️ En Linux / macOS

```
chmod +x instalar_requisitos.sh
./instalar_requisitos.sh
python3 password_manager.py
```


🪟 En Windows

Haz doble clic en instalar_requisitos.bat, o ejecuta en consola (Powershell):

```
instalar_requisitos.bat
python password_manager.py
```

👨‍💻 Uso

   Ejecuta el programa:
   
    python vaultica.py

  **O en linux/Mac:**

    python3 vaultca.py

 Registra un nuevo usuario.

   Inicia sesión.

  Puedes:

  **Añadir contraseñas manualmente.**

  **Generar contraseñas aleatorias.**

  **Ver y copiar tus contraseñas guardadas.**


📝 Archivos del Proyecto

   password_manager.py → Código principal.
    
   key.key → Clave Fernet (generada automáticamente).

   users.json → Usuarios registrados (con hashes).

   passwords.json → Contraseñas cifradas por usuario.

   instalar_requisitos.sh → Instalador para Linux/macOS.

   instalar_requisitos.bat → Instalador para Windows.

   📄 Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3.0.**
Puedes usarlo, modificarlo y distribuirlo bajo sus términos.

👨‍💻 Autor

Jaime Gálvez Martínez
📅 Proyecto iniciado: diciembre de 2024

**Muchas Gracias por usar Vaultica, y espero, que sirva de ayuda ;)**

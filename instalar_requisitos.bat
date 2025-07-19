@echo off
:: Autor: Jaime Galvez Martinez
:: Fecha: 19/07/2025
:: Script para instalar dependencias del Gestor de Contraseñas en Windows

echo 🔐 Instalador de requisitos para GNU-PasswdManager (Windows)

:: Paso 1: Verificar Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python no está instalado. Descárgalo desde https://www.python.org/downloads/
    pause
    exit /b
)

:: Paso 2: Verificar pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip no está instalado. Instalando pip...
    python -m ensurepip
)

:: Paso 3: Mostrar advertencia si no está en entorno virtual
where venv\Scripts\activate.bat >nul 2>&1
if %errorlevel% neq 0 (
    echo  No parece que estés en un entorno virtual. Se recomienda usar uno:
    echo     python -m venv venv
    echo     venv\Scripts\activate
    echo.
)

:: Paso 4: Instalar cryptography
echo 📦 Instalando cryptography...
python -m pip install --upgrade pip
python -m pip install cryptography

:: Paso 5: Verificar tkinter
:: tkinter ya viene con Python en Windows, pero probamos por si acaso
echo 🔍 Verificando tkinter...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  tkinter no está disponible. Es posible que tu instalación de Python esté incompleta.
    echo Reinstala Python desde https://www.python.org/ y asegúrate de marcar 'tcl/tk'.
) else (
    echo ✅ tkinter está disponible.
)

:: Paso 6: Crear key.key si no existe
if not exist key.key (
    echo 🔑 Generando archivo key.key...
    python -c "from cryptography.fernet import Fernet; open('key.key','wb').write(Fernet.generate_key())"
    echo ✅ Clave Fernet generada.
) else (
    echo 🔐 key.key ya existe.
)

echo ✅ Instalación completada.
pause

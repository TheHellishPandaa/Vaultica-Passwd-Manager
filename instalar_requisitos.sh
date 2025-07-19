#!/bin/bash

# Autor: Jaime Galvez Martinez
# Fecha: 19/07/2025
# Script para instalar dependencias del Gestor de Contraseñas en Python

echo "🔐 Instalador de requisitos para Vaultica-PasswdManager"

# Paso 1: Verificar Python y pip
if ! command -v python3 &> /dev/null; then
    echo "Python 3 no está instalado. Instálalo antes de continuar."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip no está instalado. Instalándolo..."
    sudo apt-get update && sudo apt-get install -y python3-pip
fi

# Paso 2: Verificar si estás en un entorno virtual
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "No estás dentro de un entorno virtual. Se recomienda usar uno con venv."
    echo "Ejemplo:"
    echo "    python3 -m venv venv"
    echo "    source venv/bin/activate"
    echo ""
fi

# Paso 3: Instalar dependencias
echo "📦 Instalando dependencias..."
pip3 install --upgrade pip
pip3 install cryptography

# Paso 4: Verificar tkinter (solo necesario en Linux, ya viene con Python en muchos casos)
echo "🔍 Verificando tkinter..."
python3 -c "import tkinter" 2>/dev/null
if [[ $? -ne 0 ]]; then
    echo "📥 Instalando tkinter..."
    sudo apt-get install -y python3-tk
else
    echo "✅ tkinter ya está instalado."
fi

# Paso 5: Crear archivo key.key si no existe
if [[ ! -f "key.key" ]]; then
    echo "🔑 Generando archivo key.key..."
    python3 -c "from cryptography.fernet import Fernet; open('key.key','wb').write(Fernet.generate_key())"
    echo "✅ Clave Fernet generada y guardada en key.key"
else
    echo "🔐 key.key ya existe. No se sobrescribe."
fi

echo "✅ Instalación completada correctamente."

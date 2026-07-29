"""
Script para generar ejecutable de ConciliaPyme Ledger Pro usando PyInstaller
Copyright 2026 © Creado por Pedro Narváez y Ariel Torres.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 50)
    print("ConciliaPyme Ledger Pro - Generador de EXE")
    print("=" * 50)
    
    # Verificar PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller encontrado: v{PyInstaller.__version__}")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Directorio base
    base_dir = Path(__file__).parent
    src_dir = base_dir / "src"
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    # Limpiar directorios previos
    if dist_dir.exists():
        print("Limpiando directorio dist/...")
        for f in dist_dir.iterdir():
            if f.is_file():
                f.unlink()
    
    if build_dir.exists():
        print("Limpiando directorio build/...")
        import shutil
        shutil.rmtree(build_dir)
    
    # Crear directorio dist si no existe
    dist_dir.mkdir(exist_ok=True)
    
    # Comando PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ConciliaPymeLedgerPro",
        "--onedir",  # Cambiar a --onefile para executable único
        "--windowed",
        "--icon=NONE",  # Agregar icono si disponible
        "--add-data", f"src{os.pathsep}src",
        "--hidden-import", "tkinter",
        "--hidden-import", "sqlite3",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        str(src_dir / "conciliapyme.py")
    ]
    
    print("\nEjecutando PyInstaller...")
    print(" ".join(cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 50)
        print("¡EXE generado exitosamente!")
        print(f"Ubicación: {dist_dir / 'ConciliaPymeLedgerPro'}")
        print("=" * 50)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR al generar EXE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

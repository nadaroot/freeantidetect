"""
Standalone single-file binary builder for Root Detect (PyInstaller).
"""

import sys
import subprocess
import shutil
from pathlib import Path

def build():
    base_dir = Path(__file__).parent.resolve()
    print("=== Сборка Root Detect в единый исполняемый файл ===")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller не установлен. Устанавливаем: pip install pyinstaller")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    entry_point = base_dir / "antidetect.py"
    ext_folder = base_dir / "rootdetect" / "extension"

    sep = ";" if sys.platform == "win32" else ":"
    add_data_arg = f"{str(ext_folder)}{sep}rootdetect/extension"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=antidetect",
        "--onefile",
        "--clean",
        f"--add-data={add_data_arg}",
        str(entry_point)
    ]

    print(f"Запуск команды сборки: {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=str(base_dir))
    
    print("\n[✓] Сборка успешно завершена!")
    dist_file = base_dir / "dist" / ("antidetect.exe" if sys.platform == "win32" else "antidetect")
    print(f"[✓] Готовый исполняемый файл находится в: {dist_file}")

if __name__ == "__main__":
    build()

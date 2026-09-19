"""
Standalone single-file binary builder for Root Detect (PyInstaller).
Supports building RootDetect-Web (Web UI) and RootDetect-CLI.
"""

import sys
import os
import argparse
import subprocess
import shutil
from pathlib import Path

def build_binary(target: str = "web"):
    base_dir = Path(__file__).parent.resolve()
    print(f"\n=== Сборка Root Detect [{target.upper()}] в единый исполняемый файл ===")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller не установлен. Устанавливаем: pip install pyinstaller")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    sep = ";" if sys.platform == "win32" else ":"
    ext_folder = base_dir / "rootdetect" / "extension"
    assets_folder = base_dir / "rootdetect" / "assets"
    
    add_data_ext = f"{str(ext_folder)}{sep}rootdetect/extension"
    add_data_assets = f"{str(assets_folder)}{sep}rootdetect/assets"

    if target == "web":
        entry_point = base_dir / "web_app.py"
        bin_name = "RootDetect-Web"
    elif target == "cli":
        entry_point = base_dir / "antidetect.py"
        bin_name = "RootDetect-CLI"
    else:
        raise ValueError(f"Unknown target: {target}")

    icon_path = None
    if sys.platform == "darwin":
        icns_file = assets_folder / "app.icns"
        if icns_file.exists():
            icon_path = str(icns_file)
    else:
        ico_file = assets_folder / "app.ico"
        if ico_file.exists():
            icon_path = str(ico_file)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        f"--name={bin_name}",
        "--onefile",
        "--clean",
        f"--add-data={add_data_ext}",
        f"--add-data={add_data_assets}",
        "--hidden-import=rich",
        "--hidden-import=rich.console",
        "--hidden-import=rich.table",
        "--hidden-import=rich.panel",
        "--hidden-import=rich.prompt",
        "--hidden-import=rich.text",
        "--hidden-import=rich.box",
        "--hidden-import=urllib.request",
        "--hidden-import=urllib.parse",
        "--hidden-import=http.server",
        "--hidden-import=json",
        "--hidden-import=sqlite3",
        "--hidden-import=threading"
    ]

    if icon_path:
        cmd.append(f"--icon={icon_path}")

    cmd.append(str(entry_point))

    print(f"Запуск команды сборки: {' '.join(cmd)}\n")
    subprocess.check_call(cmd, cwd=str(base_dir))
    
    ext = ".exe" if sys.platform == "win32" else ""
    dist_file = base_dir / "dist" / f"{bin_name}{ext}"
    print(f"\n[+] Сборка {bin_name} успешно завершена!")
    print(f"[+] Готовый исполняемый файл находится в: {dist_file}")
    return dist_file

def main():
    parser = argparse.ArgumentParser(description="Сборщик исполняемых файлов Root Detect")
    parser.add_argument("--target", choices=["web", "cli", "all"], default="web", help="Цель сборки (web, cli или all)")
    args = parser.parse_args()

    if args.target == "all":
        build_binary("web")
        build_binary("cli")
    else:
        build_binary(args.target)

if __name__ == "__main__":
    main()

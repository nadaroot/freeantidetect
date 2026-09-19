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

# Force UTF-8 on Windows and reconfigure stdout/stderr with replacement fallback
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def build_binary(target: str = "web"):
    base_dir = Path(__file__).parent.resolve()
    print(f"\n=== Building Root Detect [{target.upper()}] standalone binary ===")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[!] PyInstaller not found. Installing: pip install pyinstaller")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    sep = ";" if sys.platform == "win32" else ":"
    ext_folder = base_dir / "rootdetect" / "extension"
    assets_folder = base_dir / "rootdetect" / "assets"
    
    add_data_ext = f"{str(ext_folder)}{sep}rootdetect/extension"
    add_data_assets = f"{str(assets_folder)}{sep}rootdetect/assets"

    if target == "web":
        entry_point = base_dir / "web_app.py"
        bin_name = "RootDetect-Web"
        window_flag = "--noconsole"
    elif target == "cli":
        entry_point = base_dir / "antidetect.py"
        bin_name = "RootDetect-CLI"
        window_flag = "--console"
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
        window_flag,
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

    print(f"Running build command: {' '.join(cmd)}\n")
    subprocess.check_call(cmd, cwd=str(base_dir))
    
    ext = ".exe" if sys.platform == "win32" else ""
    dist_file = base_dir / "dist" / f"{bin_name}{ext}"
    print(f"\n[+] Build successful: {bin_name}")
    print(f"[+] Output binary: {dist_file}")
    return dist_file

def main():
    parser = argparse.ArgumentParser(description="Root Detect Standalone Binary Builder")
    parser.add_argument("--target", choices=["web", "cli", "all"], default="web", help="Build target (web, cli, or all)")
    args = parser.parse_args()

    if args.target == "all":
        build_binary("web")
        build_binary("cli")
    else:
        build_binary(args.target)

if __name__ == "__main__":
    main()

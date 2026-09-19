#!/usr/bin/env python3
"""
Root Detect - Web Interface Runner
Standalone launcher that boots the local dashboard and opens the UI in your browser.
"""

import sys
import os
import time
import subprocess
import webbrowser
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Windows console UTF-8 & ANSI color initialization
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rootdetect.web_server import start_web_server
from rootdetect.browser import find_installed_browsers

def main():
    port = 5050
    for idx, arg in enumerate(sys.argv):
        if arg in ("--port", "-p") and idx + 1 < len(sys.argv):
            try:
                port = int(sys.argv[idx + 1])
            except ValueError:
                pass

    print("=" * 60)
    print("           ROOT DETECT · WEB DASHBOARD")
    print("       Локальный автономный антидетект-браузер")
    print("=" * 60)

    try:
        server = start_web_server(port)
        actual_port = server.server_port
    except Exception as e:
        print(f"[!] Ошибка запуска веб-сервера: {e}")
        sys.exit(1)

    url = f"http://127.0.0.1:{actual_port}"
    print(f"\n[+] Веб-сервер запущен: {url}")
    print("[*] Открытие интерфейса...")

    # Try launching in App Window mode for native look & feel
    browsers = find_installed_browsers()
    app_launched = False
    for b in browsers:
        if b.get("engine") == "chromium" or any(name in b.get("path", "").lower() for name in ["chrome", "edge", "brave"]):
            try:
                subprocess.Popen(
                    [b["path"], f"--app={url}", "--window-size=1200,820"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True
                )
                app_launched = True
                break
            except Exception:
                pass

    if not app_launched:
        webbrowser.open(url)

    print("\n[+] Интерфейс открыт в браузере.")
    print("[i] Для завершения работы нажмите Ctrl + C в этом окне.")
    print("-" * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[*] Остановка сервера...")
        try:
            server.shutdown()
        except Exception:
            pass
        print("[+] Работа Root Detect завершена.")
        sys.exit(0)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Root Detect - Standalone Runner (Cross-Platform: Windows, macOS, Linux)
"""

import sys
import os
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
        # Enable Virtual Terminal Processing for ANSI colors
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from rootdetect.cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nВыход...")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n[!] Ошибка запуска программы: {e}")
        traceback.print_exc()
        if sys.platform == "win32":
            try:
                input("\nНажмите Enter для выхода...")
            except Exception:
                pass
        sys.exit(1)

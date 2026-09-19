#!/usr/bin/env python3
"""
Root Detect - Standalone Runner
"""

import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from rootdetect.cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nВыход...")
        sys.exit(0)

"""
California Tax Return Assistant

A desktop application for preparing federal (Form 1040) and
California state (Form 540) tax returns.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from src.ui import main

if __name__ == "__main__":
    main()

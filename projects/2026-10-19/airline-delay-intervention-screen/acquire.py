"""Acquire only the fingerprint-pinned official observations; never silently repin."""
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent))
from collect import collect
if __name__ == '__main__':
    collect(BASE.name)

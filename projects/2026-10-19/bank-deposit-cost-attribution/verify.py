"""Run all three verification stages for this project."""
import subprocess,sys
from pathlib import Path
base=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(base.parent/'verify_all.py'),'--project',base.name],check=True)

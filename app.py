import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "app" / "api"))
from app import app
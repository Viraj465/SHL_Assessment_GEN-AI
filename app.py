import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "app" / "api"))
from app.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
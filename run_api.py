from pathlib import Path

import uvicorn

if __name__ == "__main__":
    src_dir = str(Path(__file__).resolve().parent / "src")
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=src_dir,
    )

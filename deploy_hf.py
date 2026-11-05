"""Upload this project to a Hugging Face Space (Docker).

Usage:
    python deploy_hf.py YOUR_HF_USERNAME/agri-advisory
    python deploy_hf.py YOUR_HF_USERNAME/agri-advisory --dry-run   (only list files)

Needs: pip install huggingface_hub, and a login:
    python -c "from huggingface_hub import login; login()"
"""
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SKIP_DIRS = {".git", ".vscode", "venv", ".venv", "node_modules", "chroma_db",
             "dist", "__pycache__", "docs", "tts_lab"}
SKIP_NAMES = {".env", "README.md", "deploy_hf.py", "eval_english.txt",
              "eval_telugu.txt", "translate_debug.txt"}
SKIP_SUFFIXES = {".db", ".mp3", ".wav"}
SKIP_PDF_WORDS = ("panchangam", "test_questions")

SPACE_README = """---
title: Agri Advisory
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

Voice-based multilingual agricultural advisory (RAG + answer verification).
Source code: https://github.com/Farzana-sk/agriculture_rag_verified_advisory
"""


def ignore(directory, names):
    skipped = []
    here = Path(directory)
    for name in names:
        path = here / name
        lowered = name.lower()
        if path.is_dir() and name in SKIP_DIRS:
            skipped.append(name)
        elif path.is_file():
            if name in SKIP_NAMES or path.suffix.lower() in SKIP_SUFFIXES:
                skipped.append(name)
            elif path.suffix.lower() == ".pdf" and (
                here == ROOT or any(w in lowered for w in SKIP_PDF_WORDS)
            ):
                skipped.append(name)  # root-level reference papers, Panchangam, test PDF
    return skipped


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args:
        sys.exit(__doc__)
    repo_id = args[0]

    stage = Path(tempfile.mkdtemp(prefix="hf_stage_")) / "space"
    shutil.copytree(ROOT, stage, ignore=ignore)
    (stage / "README.md").write_text(SPACE_README, encoding="utf-8")

    files = sorted(p for p in stage.rglob("*") if p.is_file())
    total = sum(p.stat().st_size for p in files) / 1e6
    for p in files:
        print(" ", p.relative_to(stage).as_posix())
    print(f"\n{len(files)} files, {total:.1f} MB")
    if any(".env" == p.name for p in files):
        sys.exit("Refusing to upload: .env found in the upload set.")
    if dry:
        print("Dry run only. Nothing uploaded.")
        return

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(repo_id, repo_type="space", space_sdk="docker", exist_ok=True)
    api.upload_folder(folder_path=str(stage), repo_id=repo_id, repo_type="space",
                      commit_message="Deploy advisory system")
    print(f"\nUploaded. Open https://huggingface.co/spaces/{repo_id}")
    print("Now add the secret GROQ_API_KEY in the Space: Settings -> Variables and secrets.")


if __name__ == "__main__":
    main()

"""Packaging CD dimostrativo: archivio del commit e puntatore locale, nessun server."""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    os.chdir(ROOT)
    if Path(git("rev-parse", "--show-toplevel")).resolve() != ROOT:
        raise SystemExit("Inizializza Git nella cartella git-security-lab.")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise SystemExit("CD BLOCCATA: salva le modifiche in un commit prima del rilascio.")
    sha = git("rev-parse", "HEAD")
    folder = ROOT / "dist" / "releases"
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / f"{sha}.zip"
    subprocess.run(
        ["git", "archive", "--format=zip", "--output", str(archive), "HEAD", "app"],
        cwd=ROOT,
        check=True,
    )
    manifest = {"commit": sha, "artifact": f"releases/{sha}.zip", "mode": "simulation"}
    pending = ROOT / "dist" / "current.json.tmp"
    pending.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    pending.replace(ROOT / "dist" / "current.json")
    print(f"CD SIMULATA COMPLETATA: {archive.relative_to(ROOT)}")
    print("Puntatore locale: dist/current.json")


if __name__ == "__main__":
    main()

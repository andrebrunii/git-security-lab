"""Esempio volutamente vulnerabile per il laboratorio di analisi statica."""
import argparse
import subprocess


def render_report(name: str) -> str:
    # VULNERABILITA: input esterno concatenato a un comando interpretato dalla shell.
    result = subprocess.run(
        f"echo Report per: {name}",
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="?", default="Andrea")
    args = parser.parse_args()
    print(render_report(args.name))


if __name__ == "__main__":
    main()

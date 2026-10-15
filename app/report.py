"""Versione sicura: il nome viene trattato esclusivamente come testo."""
import argparse


def render_report(name: str) -> str:
    return f"Report per: {name}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="?", default="Andrea")
    args = parser.parse_args()
    print(render_report(args.name))


if __name__ == "__main__":
    main()

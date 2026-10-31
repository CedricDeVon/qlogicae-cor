
def main():
    try:
        import sys # nosec B404
        import subprocess # nosec B404
        from pathlib import Path

        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve().parent / "v3" / "app.py"),
                *sys.argv[1:],
            ],
            check=False, # nosec B603
            shell=False, # nosec B603
        )

        return result.returncode

    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

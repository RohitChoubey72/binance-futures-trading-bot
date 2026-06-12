import sys
from bot.cli import run_cli

if __name__ == "__main__":
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n[!] Execution interrupted by user. Exiting...")
        sys.exit(130)

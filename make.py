try:
    from cli import cli_instance
except ImportError:
    print("\033[91m" + "Some imports were not found. Please install all dependencies in the dev.requirements.txt file." + "\033[0m")
    exit(1)

if __name__ == "__main__":
    cli_instance()

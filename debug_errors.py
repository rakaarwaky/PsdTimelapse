from engine.tools.auto_fixer.core.runner import LinterRunner  # type: ignore[import-not-found]


def main():
    print("Collecting errors...")
    runner = LinterRunner()
    errors = runner.collect_errors()

    print(f"\nFound {len(errors)} errors:")
    for i, err in enumerate(errors, 1):
        print(f"{i}. [{err.code}] {err.file}:{err.line} - {err.message}")


if __name__ == "__main__":
    main()

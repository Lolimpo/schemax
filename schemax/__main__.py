import argparse
import json

from schemax import from_json_schema


def main() -> None:
    parser = argparse.ArgumentParser("schemax", description="Schemax cli-tool")

    commands = ["generate", "translate"]
    parser.add_argument("command", nargs="?", help=f"Available commands: {commands}")
    args, other_args = parser.parse_known_args()

    if args.command == "generate":
        parser.exit(0, "Not yet implemented")

    elif args.command == "translate":
        if len(other_args) < 1:
            parser.exit(1, "No JSON-Schema file provided")

        for file in other_args:
            try:
                with open(file, 'r') as f:
                    print(f"Translation from JSON-Schema to d42-schema for {file}:")
                    print(from_json_schema(json.load(f)), end="\n\n")
            except FileNotFoundError:
                print(f"File {file} doesn't exist", end="\n\n")
                continue


if __name__ == '__main__':
    main()

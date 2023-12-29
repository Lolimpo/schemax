import argparse
import json
from json import JSONDecodeError

from schemax import from_json_schema
from schemax._data_collector import collect_schema_data
from schemax._generator import MainGenerator


def main() -> None:
    parser = argparse.ArgumentParser("schemax", description="Schemax cli-tool")

    commands = ["generate", "translate"]
    parser.add_argument("command", nargs="?", help=f"Available commands: {commands}")
    args, other_args = parser.parse_known_args()

    if args.command == "generate":
        if len(other_args) < 1:
            parser.exit(1, "No JSON-Schema file provided")
        if len(other_args) > 1:
            parser.exit(1, "More than one JSON-Schema file provided")
        try:
            with open(other_args[0], 'r') as f:
                print("Generating schemas and interfaces from given OApi JSON-Schema...")
                schema_data = collect_schema_data(json.load(f))
                generator = MainGenerator(schema_data)
                generator.all()
                print("Successfully generated")
        except FileNotFoundError:
            print(f"File '{other_args[0]}' doesn't exist")
            exit(1)
        except JSONDecodeError:
            print(f"File '{f.name}' doesn't contain JSON")
            exit(1)
    elif args.command == "translate":
        if len(other_args) < 1:
            parser.exit(1, "No JSON-Schema file provided")

        for file in other_args:
            try:
                with open(file, 'r') as f:
                    print(f"Translation from JSON-Schema to d42-schema for {file}:")
                    print(from_json_schema(json.load(f)), end="\n\n")
            except FileNotFoundError:
                print(f"File '{file}' doesn't exist", end="\n\n")
                continue
            except JSONDecodeError:
                print(f"File '{file}' doesn't contain JSON", end='\n\n')
                continue


if __name__ == '__main__':
    main()

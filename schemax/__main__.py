import argparse
import json
from json import JSONDecodeError
from typing import Optional

import yaml

from schemax import from_json_schema
from schemax._data_collector import collect_schema_data
from schemax._generator import MainGenerator


def translate(files: str) -> None:
    if len(files) < 1:
        print("Error: No JSON-Schema file provided.")
        exit(1)

    for file in files:
        print(f"Translation from JSON-Schema to d42-schema for '{file}':")
        try:
            with open(file, "r") as f:
                print(from_json_schema(json.load(f)), end="\n\n")
        except FileNotFoundError:
            print("File doesn't exist", end="\n\n")
            continue
        except JSONDecodeError:
            print("File doesn't contain JSON", end='\n\n')
            continue


def generate(file: str, base_url: Optional[str] = None, humanize: bool = False) -> None:
    if len(file) < 1:
        print("No OpenAPI file provided")
        exit(1)
    try:
        with open(file, "r") as f:
            print("Generating schemas and interfaces from given OpenApi...")
            if f.name.endswith(".json"):
                schema_data = collect_schema_data(json.load(f))
            elif f.name.endswith(".yaml") or f.name.endswith(".yml"):
                schema_data = collect_schema_data(yaml.load(f, yaml.FullLoader))
            else:
                print(f"'{f.name}' type is not .json or .yaml file")
                exit(1)

            generator = MainGenerator(schema_data)
            generator.all()
            print("Successfully generated")
    except FileNotFoundError:
        print(f"File '{file}' doesn't exist")
        exit(1)
    except JSONDecodeError:
        print(f"File '{f.name}' doesn't contain JSON")
        exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI script with generate and translate functions")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Команда generate
    generate_parser = subparsers.add_parser("generate", help="Generate from a file")
    generate_parser.add_argument("input_file", help="Input file for generation")
    generate_parser.add_argument("--base_url", help="Base API URL for interface")
    generate_parser.add_argument(
        "--humanize", action="store_true", help="Make interface human-readable")

    # Команда translate
    translate_parser = subparsers.add_parser("translate", help="Translate from multiple files")
    translate_parser.add_argument("input_files", nargs="+", help="Input files for translation")

    args = parser.parse_args()

    if args.command == "generate":
        generate(args.input_file, args.base_url, args.humanize)
    elif args.command == "translate":
        translate(args.input_files)
    else:
        print("Unknown command")
        parser.print_help()


if __name__ == '__main__':
    main()

# CLAUDE.md - AI Assistant Guide for schemax

## Project Overview

**schemax** is a Python library that provides bidirectional translation between [d42](https://d42.sh/) schemas and [JSON Schema](https://json-schema.org/), with additional support for OpenAPI specification parsing and test code generation.

**Primary Use Cases:**
- Convert d42 schemas to JSON Schema format
- Convert JSON Schema to d42 format
- Parse OpenAPI specifications and generate test interfaces
- Generate vedro test scenarios from API specifications

**PyPI Package:** https://pypi.python.org/pypi/schemax/
**Repository:** https://github.com/Lolimpo/schemax

---

## Repository Structure

```
schemax/
├── schemax/                  # Main package directory
│   ├── __init__.py          # Public API exports (to_json_schema, from_json_schema, etc.)
│   ├── __main__.py          # CLI entry point (translate & generate commands)
│   ├── __version__.py       # Version string
│   ├── _translator.py       # d42 → JSON Schema translation logic (Visitor pattern)
│   ├── _from_json_schema.py # JSON Schema → d42 translation logic
│   ├── _data_collector.py   # OpenAPI schema parsing & SchemaData extraction
│   ├── _generator.py        # Code generation from OpenAPI (vedro tests, interfaces)
│   ├── _openapi_normalizer.py # Resolves $ref and normalizes OpenAPI schemas
│   ├── _interface.py        # Interface generation utilities
│   ├── _config.py           # Configuration handling
│   ├── supported_props.py   # Supported d42 schema properties
│   └── templates/           # Jinja2 templates for code generation
│       ├── schemas.py.j2
│       ├── schema_definition.py.j2
│       ├── api_route.py.j2
│       ├── scenario.py.j2
│       └── interfaces.py.j2
├── tests/                    # Test suite
│   ├── test_from_json_schema.py
│   └── test_to_json_schema.py
├── pyproject.toml           # Project metadata & dependencies (uv-managed)
├── uv.lock                  # Locked dependencies
├── Makefile                 # Development commands
├── README.md                # User documentation
└── LICENSE.txt              # Apache 2.0 license
```

---

## Technology Stack

### Core Dependencies
- **Python:** 3.10+ (tested on 3.10, 3.11, 3.12, 3.13)
- **d42:** Schema validation library (v2.x)
- **district42-exp-types:** Extended d42 types (v1.x)
- **jinja2:** Template engine for code generation (v3.x)
- **pyyaml:** YAML parsing (v6.x)
- **referencing:** JSON Schema reference resolution (v0.35.x)
- **vedro:** Testing framework (v1.x)
- **vedro-httpx:** HTTP testing utilities

### Development Tools
- **uv:** Fast Python package installer and resolver (replaces pip/poetry)
- **pytest:** Testing framework
- **mypy:** Static type checker (strict mode enabled)
- **ruff:** Fast Python linter and formatter
- **coverage:** Code coverage reporting
- **baby-steps:** Testing utility

---

## Development Workflow

### Setup

```bash
# Install dependencies (including dev dependencies)
make install
# or manually:
uv sync --group dev
```

### Running Tests

```bash
# Run test suite
make test
# or manually:
uv run python -m pytest

# Run tests in Docker (specify Python version)
make test-in-docker PYTHON_VERSION=3.13
```

### Linting & Type Checking

```bash
# Run linters and type checker
make lint
# This runs:
# - mypy schemax --strict
# - ruff check --fix schemax tests
```

### Full Development Cycle

```bash
# Install dependencies, lint, and test
make all

# Run everything in Docker
make all-in-docker PYTHON_VERSION=3.13
```

### Cleaning Build Artifacts

```bash
make clean  # Removes dist/, build/, *.egg-info/
```

---

## Code Style & Conventions

### Python Style (from .editorconfig)
- **Indentation:** 4 spaces (not tabs)
- **Line length:** 99 characters max
- **Line endings:** LF (Unix-style)
- **Encoding:** UTF-8
- **Final newline:** Required

### Type Hints
- **Strict typing enforced:** All code must pass `mypy --strict`
- Always include type hints for function parameters and return values
- Use `from typing import` for generic types (Dict, List, Optional, Any, etc.)
- The project includes a `py.typed` marker for PEP 561 compliance

### Naming Conventions
- **Public API:** Exported in `__init__.py` using `__all__`
- **Internal modules:** Prefixed with underscore (e.g., `_translator.py`)
- **Classes:** PascalCase (e.g., `Translator`, `SchemaData`)
- **Functions/methods:** snake_case (e.g., `to_json_schema`, `collect_schema_data`)
- **Constants:** UPPER_SNAKE_CASE (rare in this codebase)

### Module Organization
- Core translation logic uses the **Visitor pattern** (see `_translator.py`)
- Dataclasses used for structured data (see `SchemaData` in `_data_collector.py`)
- Warnings issued for unsupported schema properties

---

## Key Architectural Patterns

### 1. Visitor Pattern (d42 → JSON Schema)
The `Translator` class in `_translator.py` implements `SchemaVisitor[Any]` to traverse d42 schemas:

```python
class Translator(SchemaVisitor[Any]):
    def visit_none(self, schema: NoneSchema, **kwargs: Any) -> Dict[str, Any]:
        return {"type": "null"}

    def visit_int(self, schema: IntSchema, **kwargs: Any) -> Dict[str, Any]:
        # Translates d42 int schema to JSON Schema integer
        ...
```

**Usage:** `schema.__accept__(_translator, **kwargs)`

### 2. Recursive Normalization (JSON Schema → d42)
The `_from_json_schema` module recursively converts JSON Schema to d42:
- Handles all JSON Schema types (null, boolean, integer, number, string, array, object)
- Processes constraints (min/max, length, patterns, etc.)
- Normalizes schemas via `openapi_normalizer` (resolves $ref)

### 3. OpenAPI Processing Pipeline
`_data_collector.py` → `_generator.py`:
1. **Normalize:** Resolve all `$ref` references
2. **Collect:** Extract paths, methods, schemas into `SchemaData` objects
3. **Convert:** Translate JSON Schema → d42
4. **Generate:** Render Jinja2 templates to produce test code

### 4. CLI Architecture
`__main__.py` provides two commands:
- **translate:** Converts JSON Schema files to d42 (prints to stdout)
- **generate:** Parses OpenAPI (JSON/YAML) and generates test project structure

---

## Important Files & Their Responsibilities

| File | Purpose | Key Functions/Classes |
|------|---------|----------------------|
| `__init__.py` | Public API surface | `to_json_schema()`, `from_json_schema()`, `collect_schema_data()` |
| `_translator.py` | d42 → JSON Schema | `Translator` (visitor pattern) |
| `_from_json_schema.py` | JSON Schema → d42 | `_from_json_schema()` |
| `_data_collector.py` | OpenAPI parsing | `SchemaData` dataclass, `collect_schema_data()` |
| `_generator.py` | Code generation | `MainGenerator` (uses Jinja2 templates) |
| `_openapi_normalizer.py` | $ref resolution | `openapi_normalizer()` |
| `supported_props.py` | Schema property validation | Property type definitions |

---

## Testing Conventions

### Test Files
- `tests/test_to_json_schema.py` - Tests d42 → JSON Schema conversion
- `tests/test_from_json_schema.py` - Tests JSON Schema → d42 conversion

### Running Tests
Tests use **pytest** and **baby-steps** for BDD-style testing:

```bash
uv run python -m pytest
# With coverage:
uv run coverage run -m pytest
uv run coverage report
```

### Test Principles
- Test both directions of translation (bidirectional correctness)
- Cover edge cases (empty schemas, nested structures, constraints)
- Validate against JSON Schema spec compliance

---

## CI/CD Pipeline

### GitHub Actions Workflows

**`.github/workflows/test.yml`** (runs on every push):
- **Matrix testing:** Python 3.10, 3.11, 3.12, 3.13
- **Steps:**
  1. Checkout code
  2. Install uv (latest)
  3. Install Python version
  4. Run `make install`
  5. Run `make lint` (mypy + ruff)
  6. Run `make test` (pytest)

**`.github/workflows/publish.yml`** (assumed for PyPI releases):
- Likely triggers on tags/releases
- Builds and publishes to PyPI

---

## Common Development Tasks

### Adding Support for a New d42 Type

1. **Update `_translator.py`:**
   - Add a new `visit_<type>()` method
   - Map d42 properties to JSON Schema properties

2. **Update `_from_json_schema.py`:**
   - Add handling for the corresponding JSON Schema type
   - Convert back to d42

3. **Update `supported_props.py`:**
   - Define supported properties for the type

4. **Add tests:**
   - Add test cases to `tests/test_to_json_schema.py`
   - Add test cases to `tests/test_from_json_schema.py`

5. **Update README.md:**
   - Mark the feature as ✅ in the supported types table

### Adding a New CLI Command

1. Edit `__main__.py`:
   - Add a subparser in `main()`
   - Implement the command function
   - Handle file I/O and error cases

2. Update `pyproject.toml` if needed (entry points)

3. Test manually:
   ```bash
   uv run schemax <new-command> <args>
   ```

### Modifying Code Generation Templates

1. Edit files in `schemax/templates/*.j2`
2. Templates use **Jinja2 syntax**
3. Context variables come from `SchemaData` objects
4. Test by running `schemax generate` on sample OpenAPI files

---

## Git Conventions

### Branch Protection
- Work on feature branches (named `claude/...` for AI-assisted work)
- Main branch is protected (see gitStatus context)

### Commit Messages
- Use conventional commit style where appropriate
- Be descriptive about what changed and why

### Ignored Files (`.gitignore`)
- Python artifacts: `__pycache__/`, `*.pyc`, `dist/`, `build/`
- Virtual environments: `venv/`, `.venv/`
- IDE configs: `.idea/`, `.vscode/`
- Debug files: `sandbox.py`, `schema*.json`, `schema*.yml`
- Generated output: `interfaces/`, `scenarios/`, `schemas/`

---

## API Usage Examples

### Converting d42 to JSON Schema

```python
from schemax import to_json_schema
from d42 import schema

# Define a d42 schema
user_schema = schema.dict({
    "id": schema.int.min(1),
    "name": schema.str.len(1, 50),
    "email": schema.str.regex(r"^[\w\.-]+@[\w\.-]+\.\w+$"),
    "age": schema.int.min(0).max(120),
})

# Convert to JSON Schema
json_schema = to_json_schema(user_schema, title="User")
# Result includes $schema and title fields
```

### Converting JSON Schema to d42

```python
from schemax import from_json_schema

json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}

d42_schema = from_json_schema(json_schema)
```

### Parsing OpenAPI Specifications

```python
import yaml
from schemax import collect_schema_data

with open("openapi.yaml") as f:
    spec = yaml.load(f, yaml.FullLoader)
    schema_data_list = collect_schema_data(spec)

    for item in schema_data_list:
        print(f"{item.http_method.upper()} {item.path}")
        print(f"Response schema: {item.response_schema_d42}")
```

### CLI Usage

```bash
# Translate JSON Schema to d42
schemax translate schema.json

# Generate test suite from OpenAPI
schemax generate openapi.yaml --base-url="https://api.example.com" --humanize
```

---

## Troubleshooting & Known Limitations

### Unsupported Features
- **d42 → JSON Schema:**
  - `schema.bytes` (JSON Schema has no bytes type)
  - `schema.float.precision()` (planned)
  - `schema.datetime` (planned)

- **JSON Schema → d42:**
  - `multipleOf` (numeric multiples)
  - `format` (string formats like email, date-time)
  - `patternProperties` (object patterns)
  - `uniqueItems` (array uniqueness)
  - `propertyNames`, `minProperties`, `maxProperties`

### Warnings
- The library emits warnings for unsupported properties
- Regex escape sequences may not translate perfectly (JSON Schema regex != Python regex)

### Common Issues
1. **Missing $ref resolution:** Always run schemas through `openapi_normalizer` first
2. **Type mismatches:** Ensure d42 schemas are properly constructed before translation
3. **File encoding:** OpenAPI files must be valid JSON or YAML

---

## Dependencies & Version Constraints

### Production Dependencies
```toml
d42 = ">=2.0.0,<3.0.0"
district42-exp-types = ">=1.0.0,<2.0.0"
jinja2 = ">=3.1.5,<4.0.0"
niltype = ">=0.3.4,<2.0.0"
pyyaml = ">=6.0.1,<7.0.0"
referencing = ">=0.35.1,<1.0.0"
vedro = ">=1.0.0,<2.0.0"
vedro-httpx = ">=0.0.1,<1.0.0"
```

### Dev Dependencies (locked versions)
```toml
baby-steps = "1.3.1"
coverage = "7.6.10"
pytest = "8.3.4"
mypy = "1.14.1"
ruff = "0.12.7"
types-jsonschema = "4.23.0.20241208"
types-pyyaml = "6.0.12.20241230"
```

---

## AI Assistant Best Practices

### When Making Changes

1. **Always run linting after code changes:**
   ```bash
   make lint
   ```

2. **Run tests to verify correctness:**
   ```bash
   make test
   ```

3. **Update type hints:**
   - All new functions must have complete type annotations
   - Run `mypy schemax --strict` to verify

4. **Update documentation:**
   - Modify README.md if adding new features
   - Update supported types tables
   - Keep this CLAUDE.md file current

5. **Follow the existing patterns:**
   - Use Visitor pattern for schema traversal
   - Use dataclasses for structured data
   - Emit warnings for unsupported features (don't fail silently)

### Before Committing

- [ ] Code passes `make lint` (mypy + ruff)
- [ ] All tests pass (`make test`)
- [ ] Type hints are complete and correct
- [ ] No new warnings introduced (unless necessary)
- [ ] Documentation updated if needed
- [ ] CHANGELOG or commit message describes changes

### Understanding the Codebase

- Start with `__init__.py` to understand the public API
- Read `_translator.py` to understand d42 → JSON Schema
- Read `_from_json_schema.py` to understand JSON Schema → d42
- Check `tests/` for usage examples and edge cases
- Consult d42 docs at https://d42.sh/docs/ for schema semantics
- Consult JSON Schema docs at https://json-schema.org/ for spec details

---

## Additional Resources

- **d42 Documentation:** https://d42.sh/docs/
- **JSON Schema Specification:** https://json-schema.org/
- **OpenAPI Specification:** https://swagger.io/specification/
- **uv Documentation:** https://github.com/astral-sh/uv
- **vedro Testing Framework:** https://vedro.io/

---

## Questions & Support

For issues or questions:
- **GitHub Issues:** https://github.com/Lolimpo/schemax/issues
- **Maintainer:** Nikita Mikheev (thelol1mpo@gmail.com)

---

**Last Updated:** 2025-11-17
**Document Version:** 1.0
**schemax Version:** Based on current main branch state

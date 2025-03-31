# JSON Parser Project

## Overview
This project provides a simple Python script to parse a JSON file and extract specific values, such as access tokens and expiration times.

## Project Structure
```
project_root/
│-- data/
│   ├── myfile_12225259.json
│-- examples/
│   ├── main.py
│-- src/
│   ├── __init__.py
│   ├── parse_json.py
│-- .gitignore
│-- README.md
```

## Installation
Ensure you have Python 3.10 installed. You may also create a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

## Usage
Run the script from the project root to avoid module import issues:
```sh
python -m examples.main
```

Alternatively, set the `PYTHONPATH` to include the project root:
```sh
export PYTHONPATH=$(pwd)
python examples/main.py
```

## Troubleshooting
If you encounter `ModuleNotFoundError: No module named 'src'`, try one of the following solutions:
1. Run the script using `python -m examples.main` from the project root.
2. Set `PYTHONPATH` before execution.
3. Modify `sys.path` in `main.py`:
    ```python
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from src import parse_json
    ```

## License
This project is open-source and available for modification and use.


PYTHON_FILES = `(find . -type f -iname "*.py" -not -path "./.venv/*")`

update:
	uv pip install --upgrade .

ruff:
	uvx ruff check $(PYTHON_FILES)

ruff-fix:
	uvx ruff check $(PYTHON_FILES) --fix
	
.PHONY: run run-% requirements requirements-%
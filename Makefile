PYTHON_FILES = `(find . -type f -iname "*.py" -not -path "./.venv/*")`

MAKEFLAGS += --no-print-directory

update:
	uv pip install --upgrade .

RUNS = $(shell find src -mindepth 1 -maxdepth 1 -type d -not -name "common" -exec test -f {}/Makefile \; -print | xargs -n1 basename)

run-%:
	@cd src/$(@:run-%=%) && $(MAKE) run

run:
	@$(MAKE) $(addprefix run-,$(RUNS))

ruff:
	uvx ruff check $(PYTHON_FILES)

ruff-fix:
	uvx ruff check $(PYTHON_FILES) --fix
	
.PHONY: run run-% requirements requirements-%
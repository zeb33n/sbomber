SPDX_FILE ?= ""

install:
	uv pip install .

sbomber: install
	uv run sbomber $(SPDX_FILE)

build: sbomber
	uv run zensical build --clean

serve: build
	uv run python -m http.server -d site

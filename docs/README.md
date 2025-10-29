# Documentation

This directory contains the documentation for the Snakemake ESM-Tools wrappers.

## Building the Documentation

### Prerequisites

Install documentation dependencies:

```bash
pip install -r requirements.txt
```

### Build with Sphinx

```bash
cd docs
make html
```

Output will be in `_build/html/`. Open `_build/html/index.html` in a browser.

### Build with Jupyter Book

```bash
jupyter-book build docs/
```

Output will be in `docs/_build/html/`.

### Clean Build Files

```bash
make clean
```

## Documentation Structure

- `index.md` - Main landing page
- `guides/` - User guides and tutorials
  - `installation.md` - Installation instructions
  - `quickstart.md` - Quick start guide
  - `esm_master_usage.md` - esm_master wrapper guide
  - `esm_runscripts_usage.md` - esm_runscripts wrapper guide
  - `complete_workflow.md` - Complete workflow example
- `api/` - API reference with autodoc
  - `esm_master_wrapper.md` - esm_master API
  - `esm_runscripts_wrapper.md` - esm_runscripts API
  - `esm_runscripts_helper.md` - Helper module API
- `examples/` - Usage examples
  - `basic_install.md` - Basic installation
  - `simulation_workflow.md` - Simulation workflow
  - `advanced_usage.md` - Advanced patterns

## Auto-generated API Documentation

The API documentation uses Sphinx autodoc to automatically extract docstrings from:
- `esm_master/wrapper.py`
- `esm_runscripts/wrapper.py`
- `esm_runscripts/helper.py`

Docstrings are parsed using Napoleon for Google/NumPy style formatting.

## Jupyter Book Configuration

- `_config.yml` - Jupyter Book configuration
- `_toc.yml` - Table of contents
- `conf.py` - Sphinx configuration

## Contributing

When adding new features:
1. Update docstrings in the Python modules
2. Add usage examples to the guides
3. Rebuild documentation to verify
4. Commit both code and documentation changes

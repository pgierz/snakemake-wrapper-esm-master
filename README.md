# Snakemake Wrapper: ESM-Master Install

A [Snakemake](https://snakemake.readthedocs.io) wrapper for installing Earth System Models using [esm-tools](https://github.com/esm-tools/esm_tools) `esm-master` command.

## Overview

This wrapper executes the `esm-master install-<model>-<version>` command, which downloads, configures, and compiles Earth System Models as part of a Snakemake workflow.

The `install` meta-command performs three operations:
1. **get**: Downloads model source code from repositories
2. **conf**: Configures the model for compilation
3. **comp**: Compiles the model binaries

## Usage

### Basic Example

```python
rule install_model:
    output:
        touch("models/awicm-3.0/.installed")
    params:
        model="awicm",
        version="3.0",
    log:
        "logs/esm_master/awicm-3.0.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/"
```

### With Additional Options

```python
rule install_model_verbose:
    output:
        touch("models/fesom-2.0/.installed")
    params:
        model="fesom",
        version="2.0",
        extra="--verbose --check"  # Pass additional esm-master flags
    log:
        "logs/esm_master/fesom-2.0.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/"
```

### Testing Locally

To test the wrapper locally before publishing, use the `file://` protocol:

```python
rule install_test_model:
    output:
        touch("models/tux-1.0/.installed")
    params:
        model="tux",
        version="1.0",
    log:
        "logs/esm_master/tux-1.0.log"
    wrapper:
        "file:///path/to/snakemake-wrapper-esm-master"
```

Then run:
```bash
# Test the wrapper
snakemake -s your_snakefile.smk --use-conda -c1

# Or cd to the test directory
cd test/
snakemake --use-conda -c1
```

## Parameters

### Required Parameters

- **model** (str): Name of the Earth System Model to install (e.g., "awicm", "fesom", "tux")
- **version** (str): Version of the model to install (e.g., "3.0", "2.0", "1.0")

### Optional Parameters

- **extra** (str): Additional command-line arguments to pass to `esm-master` (e.g., "--verbose", "--check", "--ignore-errors")

## Output

The wrapper doesn't produce specific output files by design, as `esm-master` installs models into its configured directory structure. Use `touch()` to create a marker file indicating successful installation:

```python
output:
    touch("models/{model}-{version}/.installed")
```

## Log Files

All stdout and stderr from the `esm-master` command are captured in the specified log file:

```python
log:
    "logs/esm_master/{model}-{version}.log"
```

## Requirements

### Dependencies

- **esm-tools** v6.59.0 (installed from git via pip)
- **Python** >= 3.8

The wrapper automatically creates a conda environment with these dependencies.

### ESM-Tools Configuration

The wrapper requires a properly configured esm-tools environment. Ensure that:
- You have access to the required model repositories
- Authentication credentials are set up (for private repositories)
- The target compute environment is supported by esm-tools

## Available Models

Common models supported by esm-tools include:
- **awicm** - AWI Climate Model
- **fesom** - Finite Element Sea Ice-Ocean Model
- **echam** - ECHAM atmospheric model
- **tux** - Test model (downloads a simple file via curl)

For a complete list of available models and versions, consult the [esm-tools documentation](https://esm-tools.readthedocs.io) or run:
```bash
esm-master --list_all_targets
```

## Example Workflow

Here's a complete example workflow that installs multiple models:

```python
MODELS = {
    "tux": "1.0",
    "awicm": "3.0",
    "fesom": "2.0"
}

rule all:
    input:
        expand("models/{model}-{version}/.installed",
               zip,
               model=MODELS.keys(),
               version=MODELS.values())

rule install_model:
    output:
        touch("models/{model}-{version}/.installed")
    params:
        model="{model}",
        version="{version}",
    log:
        "logs/esm_master/{model}-{version}.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/"
```

## Notes

- The `esm-master install` command performs a full installation (download, configure, compile)
- Installation locations are determined by esm-tools configuration
- For large models, compilation may take significant time and resources
- Use the `tux-1.0` test model for quick validation of the wrapper

## License

MIT License

## Author

Paul Gierz (paul.gierz@awi.de)

## Links

- [esm-tools GitHub](https://github.com/esm-tools/esm_tools)
- [esm-tools Documentation](https://esm-tools.readthedocs.io)
- [Snakemake Wrappers](https://snakemake-wrappers.readthedocs.io)

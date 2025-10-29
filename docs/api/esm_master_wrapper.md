# esm_master Wrapper API

This page documents the `esm_master` wrapper - a Snakemake wrapper that installs ESM-Tools climate models.

## Overview

The esm_master wrapper is a thin execution layer that:
- Extracts parameters from Snakemake context (model, version, subcommand)
- Constructs the appropriate esm_master command
- Executes the command with proper logging

Unlike the esm_runscripts wrapper, esm_master does not require a separate helper module since it has no complex logic or functions to extract. It's designed to be executed by Snakemake and relies on the injected `snakemake` object for parameters and logging.

## Wrapper Parameters

The `esm_master` wrapper accepts the following parameters through Snakemake's `params:` directive:

### Required Parameters

**model** : str
:   Name of the Earth System Model (e.g., "awicm", "fesom", "echam")

**version** : str
:   Version of the model (e.g., "3.0", "2.0", "1.0")

### Optional Parameters

**subcommand** : str, default="install"
:   ESM-Master operation to perform:
    - `get`: Download model source code
    - `conf`: Configure model for compilation
    - `comp`: Compile model binaries
    - `clean`: Clean build artifacts
    - `install`: Complete installation (get + conf + comp)
    - `recomp`: Reconfigure and recompile

**extra** : str, default=""
:   Additional command-line arguments to pass to `esm_master`

## Usage Examples

### Basic Installation

```python
rule install_model:
    output:
        touch("models/awicm-3.0/.installed")
    params:
        model="awicm",
        version="3.0",
    log:
        "log/esm_master/awicm-3.0-install.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

### Download Only

```python
rule download_model:
    output:
        touch("models/fesom-2.0/.downloaded")
    params:
        subcommand="get",
        model="fesom",
        version="2.0",
    log:
        "log/esm_master/fesom-2.0-get.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

### With Extra Arguments

```python
rule install_verbose:
    output:
        touch("models/tux-1.0/.installed")
    params:
        model="tux",
        version="1.0",
        extra="--verbose --check"
    log:
        "log/esm_master/tux-1.0-install.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

## Environment

The wrapper automatically creates a conda environment with:

- Python 3.10
- esm-tools v6.59.2 (from git)
- Required build dependencies

## Command Execution

The wrapper constructs and executes:

```bash
esm_master {subcommand}-{model}-{version} {extra}
```

For example:
```bash
esm_master install-awicm-3.0
esm_master get-fesom-2.0
esm_master comp-echam-6.3
```

## Return Codes

- **0**: Success
- **Non-zero**: Failure (see log file for details)

## Error Handling

The wrapper will fail if:
- Required parameters are missing
- esm_master command fails
- Model/version combination is invalid
- Git authentication fails (for private repos)

Check the log file specified in the `log:` directive for detailed error messages.

## Related

- [esm_runscripts Wrapper API](esm_runscripts_wrapper.md)
- [esm_master Usage Guide](../guides/esm_master_usage.md)

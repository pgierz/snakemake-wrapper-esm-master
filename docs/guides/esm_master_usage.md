# esm_master Wrapper Usage Guide

Detailed guide for using the `esm_master` wrapper to install and manage Earth System Models.

## Overview

The `esm_master` wrapper provides Snakemake integration for all esm_master subcommands:

- **get**: Download model source code
- **conf**: Configure model for compilation
- **comp**: Compile model binaries
- **clean**: Clean build artifacts
- **install**: Complete installation (get + conf + comp)
- **recomp**: Reconfigure and recompile

## Basic Usage

### Complete Installation (Default)

The simplest usage installs a complete model:

```python
rule install_awicm:
    output:
        touch("models/awicm-3.0/.installed")
    params:
        model="awicm",
        version="3.0"
    log:
        "log/esm_master/awicm-3.0.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

This executes:
```bash
esm_master install-awicm-3.0
```

### Staged Installation

Break installation into separate steps for better control:

```python
# Step 1: Download
rule download_model:
    output: touch("models/{model}-{version}/.downloaded")
    params:
        subcommand="get",
        model="{model}",
        version="{version}"
    log: "log/esm_master/{model}-{version}-get.log"
    wrapper: "file://esm_master"

# Step 2: Configure
rule configure_model:
    input: "models/{model}-{version}/.downloaded"
    output: touch("models/{model}-{version}/.configured")
    params:
        subcommand="conf",
        model="{model}",
        version="{version}"
    log: "log/esm_master/{model}-{version}-conf.log"
    wrapper: "file://esm_master"

# Step 3: Compile
rule compile_model:
    input: "models/{model}-{version}/.configured"
    output: touch("models/{model}-{version}/.compiled")
    params:
        subcommand="comp",
        model="{model}",
        version="{version}"
    log: "log/esm_master/{model}-{version}-comp.log"
    wrapper: "file://esm_master"
```

## Advanced Usage

### Multiple Models

Install multiple models using wildcards:

```python
MODELS = {
    "awicm": "3.0",
    "fesom": "2.0",
    "echam": "6.3"
}

rule all:
    input:
        expand("models/{model}-{version}/.installed",
               zip, model=MODELS.keys(), version=MODELS.values())

rule install_any_model:
    output: touch("models/{model}-{version}/.installed")
    params:
        model="{model}",
        version="{version}"
    log: "log/esm_master/{model}-{version}.log"
    wrapper: "file://esm_master"
```

### Extra Arguments

Pass additional flags to esm_master:

```python
rule install_verbose:
    output: touch("models/tux-1.0/.installed")
    params:
        model="tux",
        version="1.0",
        extra="--verbose --check"
    log: "log/esm_master/tux-1.0-verbose.log"
    wrapper: "file://esm_master"
```

Executes:
```bash
esm_master install-tux-1.0 --verbose --check
```

### Recompilation

Recompile after source changes:

```python
rule recompile_model:
    input: "src/my_modifications.f90"
    output: touch("models/awicm-3.0/.recompiled")
    params:
        subcommand="recomp",
        model="awicm",
        version="3.0"
    log: "log/esm_master/awicm-3.0-recomp.log"
    wrapper: "file://esm_master"
```

### Clean Build

Remove build artifacts:

```python
rule clean_model:
    output: touch("models/fesom-2.0/.cleaned")
    params:
        subcommand="clean",
        model="fesom",
        version="2.0"
    log: "log/esm_master/fesom-2.0-clean.log"
    wrapper: "file://esm_master"
```

## Parameters Reference

### Required Parameters

**model** (str)
:   Model identifier (e.g., "awicm", "fesom", "echam")

**version** (str)
:   Version string (e.g., "3.0", "2.0", "6.3")

### Optional Parameters

**subcommand** (str, default="install")
:   Operation: get, conf, comp, clean, install, recomp

**extra** (str, default="")
:   Additional esm_master command-line arguments

## Available Models

Common models include:

| Model | Description | Typical Versions |
|-------|-------------|------------------|
| awicm | AWI Climate Model | 3.0, 2.1 |
| fesom | FESOM Ocean Model | 2.0, 2.1, 2.5 |
| echam | ECHAM Atmosphere | 6.3 |
| tux | Test Model | 1.0 |

Check available models:
```bash
esm_master --list_all_targets
```

## Troubleshooting

### Git Authentication Issues

If installation hangs during download:

1. Check git authentication is configured
2. See [Installation Guide](installation.md#git-authentication)
3. Test: `git ls-remote https://github.com/esm-tools/esm_tools.git`

### Compilation Failures

Check the log file for specific errors:

```bash
tail -100 log/esm_master/awicm-3.0.log
```

Common issues:
- Missing compilers or libraries
- Incorrect module environment
- Insufficient disk space

### Model Not Found

Verify model/version exists:
```bash
esm_master --list_all_targets | grep awicm
```

## Best Practices

### 1. Use Marker Files

Always create marker files with `touch()`:

```python
output: touch("models/{model}-{version}/.installed")
```

### 2. Separate Download from Compilation

For expensive operations, split into stages:

```python
rule download: ...  # Fast, can retry easily
rule configure: ...  # Fast
rule compile: ...   # Slow, benefits from caching
```

### 3. Log Everything

Always specify log files:

```python
log: "log/esm_master/{model}-{version}-{subcommand}.log"
```

### 4. Test with tux Model

Validate workflows with lightweight test model:

```python
rule test:
    params:
        model="tux",
        version="1.0"
```

## Related

- [API Reference](../api/esm_master_wrapper.md)
- [esm_runscripts Usage](esm_runscripts_usage.md)
- [Complete Workflow Guide](complete_workflow.md)

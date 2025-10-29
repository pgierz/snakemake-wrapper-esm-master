# Quick Start Guide

Get started with the ESM-Tools Snakemake wrappers in 5 minutes.

## Basic Workflow

This guide shows a complete workflow: install a model and run a simulation.

### 1. Create a Snakefile

Create `Snakefile` in your project directory:

```python
from esm_runscripts.helper import get_resources

# Target: complete workflow
rule all:
    input:
        "results/my_experiment_complete.done"

# Step 1: Install the model
rule install_model:
    output:
        touch("models/awicm-3.0/.installed")
    params:
        model="awicm",
        version="3.0"
    log:
        "log/install_awicm.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"

# Step 2: Run the simulation
rule run_simulation:
    input:
        "models/awicm-3.0/.installed"
    output:
        touch("results/my_experiment_complete.done")
    params:
        runscript="awicm_config.yaml",
        task="compute",
        expid="my_experiment"
    resources:
        **get_resources("awicm_config.yaml", "compute", expid="my_experiment")
    log:
        "log/run_simulation.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"
```

### 2. Create Model Configuration

Create `awicm_config.yaml` with your model parameters:

```yaml
general:
  account: "ab1234"
  compute_time: "01:00:00"

computer:
  name: "levante"
  partition: "compute"

awicm:
  version: "3.0"
  # ... additional model configuration
```

### 3. Run the Workflow

```bash
# Dry run to check
snakemake -n

# Execute with conda
snakemake --use-conda -c1

# Or with multiple cores
snakemake --use-conda -c4
```

## What Happens

1. **Model Installation** (`esm_master`):
   - Conda environment created with esm-tools
   - Model source downloaded
   - Model configured and compiled
   - Marker file created: `models/awicm-3.0/.installed`

2. **Resource Extraction** (`get_resources()`):
   - Runs `esm_runscripts --check`
   - Parses `finished_config.yaml`
   - Extracts nodes, tasks, memory, runtime
   - Returns dict for Snakemake resources

3. **Simulation Execution** (`esm_runscripts`):
   - Generates run script
   - Extracts executable content
   - Executes within Snakemake environment
   - Creates completion marker

## Quick Examples

### Test Model Installation

Test with the lightweight `tux` model:

```python
rule test_install:
    output: touch("test/.installed")
    params:
        model="tux",
        version="1.0"
    log: "log/test.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

Run:
```bash
snakemake --use-conda -c1
```

### Download Only (No Compilation)

```python
rule download_only:
    output: touch("models/fesom-2.0/.downloaded")
    params:
        subcommand="get",
        model="fesom",
        version="2.0"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

### Multiple Simulation Phases

```python
from esm_runscripts.helper import get_resources

rule prepcompute:
    output: touch("results/{expid}_prep.done")
    params:
        runscript="config.yaml",
        task="prepcompute",
        expid="{expid}"
    resources:
        **get_resources("config.yaml", "prepcompute", expid="{expid}")
    wrapper:
        "file://esm_runscripts"

rule compute:
    input: "results/{expid}_prep.done"
    output: touch("results/{expid}_compute.done")
    params:
        runscript="config.yaml",
        task="compute",
        expid="{expid}",
        reuse_config=True
    resources:
        **get_resources("config.yaml", "compute", expid="{expid}")
    wrapper:
        "file://esm_runscripts"

rule tidy:
    input: "results/{expid}_compute.done"
    output: touch("results/{expid}_tidy.done")
    params:
        runscript="config.yaml",
        task="tidy",
        expid="{expid}",
        reuse_config=True
    resources:
        **get_resources("config.yaml", "tidy", expid="{expid}")
    wrapper:
        "file://esm_runscripts"
```

## Common Patterns

### Wildcard Models

```python
MODELS = {"awicm": "3.0", "fesom": "2.0"}

rule all:
    input:
        expand("models/{model}-{version}/.installed",
               zip, model=MODELS.keys(), version=MODELS.values())

rule install:
    output: touch("models/{model}-{version}/.installed")
    params:
        model="{model}",
        version="{version}"
    wrapper:
        "file://esm_master"
```

### Configuration Overrides

```python
rule run_with_override:
    output: touch("results/exp_modified.done")
    params:
        runscript="base_config.yaml",
        task="compute",
        expid="exp_modified",
        modify_config="overrides.yaml"
    resources:
        **get_resources("base_config.yaml", "compute",
                       expid="exp_modified", modify_config="overrides.yaml")
    wrapper:
        "file://esm_runscripts"
```

## Next Steps

- [Detailed Installation Guide](installation.md)
- [esm_master Usage](esm_master_usage.md)
- [esm_runscripts Usage](esm_runscripts_usage.md)
- [Complete Workflow Examples](complete_workflow.md)

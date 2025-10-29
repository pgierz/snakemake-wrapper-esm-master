# esm_runscripts Wrapper API

This page documents the `esm_runscripts` wrapper - a Snakemake wrapper that executes ESM-Tools climate model simulations.

## Overview

The wrapper consists of two components:

1. **wrapper.py** - Thin execution layer that Snakemake runs. This file:
   - Extracts parameters from Snakemake context
   - Calls esm_runscripts to generate configuration
   - Locates and executes the generated run script
   - Handles logging and cleanup

2. **helper.py** - Importable library with all function definitions. See [esm_runscripts Helper API](esm_runscripts_helper.md) for complete function documentation.

The wrapper.py file is designed to be executed by Snakemake and relies on the injected `snakemake` object for parameters, resources, and logging.

## Wrapper Parameters

The `esm_runscripts` wrapper accepts the following parameters through Snakemake's `params:` directive:

### Required Parameters

**runscript** : str
:   Path to ESM runscript YAML file containing model configuration

**task** : str
:   Phase to execute. Must be one of:
    - `prepcompute`: Prepare files and environment before computation
    - `compute`: Execute the coupled model simulation
    - `tidy`: Post-run cleanup and file management
    - `post`: Post-processing and data analysis

**expid** : str, default="test"
:   Experiment identifier for organizing outputs

### Optional Parameters

**reuse_config** : bool, default=False
:   If True, skip config generation and reuse existing configuration

**modify_config** : str, optional
:   Path to YAML file with configuration overrides

**current_date** : str, optional
:   Specify current simulation date (format depends on model)

**extra** : str, default=""
:   Additional command-line arguments to pass to esm_runscripts

## Resources

The wrapper requires Snakemake resource specifications. Use the helper function:

```python
from esm_runscripts.helper import get_resources

resources:
    **get_resources("awicm.yaml", "compute", expid="exp001")
```

This automatically extracts:
- **nodes**: Number of compute nodes
- **tasks**: Number of MPI tasks
- **mem_mb**: Memory per task in MB
- **runtime**: Wall time in minutes
- **partition**: SLURM partition (if specified)
- **account**: SLURM account (if specified)

## Usage Examples

### Basic Compute Phase

```python
from esm_runscripts.helper import get_resources

rule compute_phase:
    output:
        touch("results/exp001_compute.done")
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp001")
    log:
        "log/esm_runscripts/exp001-compute.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"
```

### Complete Simulation Workflow

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
        reuse_config=True  # Reuse config from prepcompute
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

### With Configuration Override

```python
rule compute_modified:
    output: touch("results/exp002_compute.done")
    params:
        runscript="base_config.yaml",
        task="compute",
        expid="exp002",
        modify_config="overrides.yaml"  # Apply modifications
    resources:
        **get_resources("base_config.yaml", "compute",
                       expid="exp002", modify_config="overrides.yaml")
    wrapper:
        "file://esm_runscripts"
```

## Execution Flow

1. **Configuration Generation** (if `reuse_config=False`):
   ```bash
   esm_runscripts --check {runscript} -t {task} -e {expid}
   ```
   Generates configuration and `.run` script file

2. **Script Location**: Finds generated `.run` file in:
   - `{expid}/scripts/`
   - `scripts/`
   - Current directory

3. **Content Extraction**: Parses `.run` file and removes:
   - SLURM directives (`#SBATCH`)
   - Batch submission commands (`sbatch`)

4. **Execution**: Runs extracted content in Snakemake's allocated environment:
   ```bash
   bash {expid}_*_snakemake.sh
   ```

## Environment

The wrapper automatically creates a conda environment with:

- Python 3.10
- esm-tools v6.59.2
- **herrkunft** - YAML provenance tracking library

## Provenance Tracking

The wrapper uses the [herrkunft library](https://pypi.org/project/herrkunft/) for YAML parsing, which provides:

- Automatic tracking of configuration value origins
- History of all modifications through inheritance
- Source file and line number tracking
- Transparent YAML loading and dumping

```python
import herrkunft as yaml

# Load with automatic provenance tracking
config = yaml.load(open("config.yaml"))

# Configuration now includes metadata about origins
```

## Error Handling

The wrapper will fail if:
- Required parameters are missing
- Runscript file doesn't exist
- esm_runscripts configuration generation fails
- Generated `.run` script cannot be found
- Script execution fails

Check the log file for detailed error messages.

## Related

- [esm_runscripts Helper API](esm_runscripts_helper.md)
- [esm_runscripts Usage Guide](../guides/esm_runscripts_usage.md)
- [herrkunft Documentation](https://herrkunft.readthedocs.io)

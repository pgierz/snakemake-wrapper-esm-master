# esm_runscripts Wrapper Usage Guide

Detailed guide for using the `esm_runscripts` wrapper to run Earth System Model simulations.

## Overview

The `esm_runscripts` wrapper provides a sophisticated two-stage approach for running simulations:

1. **Resource Extraction**: Automatically determine SLURM requirements
2. **Execution**: Run simulation phases within Snakemake's resource management

## Key Features

- Automatic resource detection from configuration
- YAML provenance tracking with [herrkunft](https://pypi.org/project/herrkunft/)
- Support for all simulation phases: prepcompute, compute, tidy, post
- Configuration reuse across phases
- Seamless Snakemake integration

## Basic Usage

### Single Compute Phase

```python
from esm_runscripts.helper import get_resources

rule compute:
    output:
        touch("results/exp001_compute.done")
    params:
        runscript="awicm_config.yaml",
        task="compute",
        expid="exp001"
    resources:
        **get_resources("awicm_config.yaml", "compute", expid="exp001")
    log:
        "log/exp001-compute.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"
```

### Complete Simulation Workflow

Run all phases in sequence:

```python
from esm_runscripts.helper import get_resources

rule all:
    input: "results/{expid}_complete.done"

rule prepcompute:
    output: touch("results/{expid}_prep.done")
    params:
        runscript="config.yaml",
        task="prepcompute",
        expid="{expid}"
    resources:
        **get_resources("config.yaml", "prepcompute", expid="{expid}")
    log: "log/{expid}-prep.log"
    wrapper: "file://esm_runscripts"

rule compute:
    input: "results/{expid}_prep.done"
    output: touch("results/{expid}_compute.done")
    params:
        runscript="config.yaml",
        task="compute",
        expid="{expid}",
        reuse_config=True  # Reuse from prepcompute
    resources:
        **get_resources("config.yaml", "compute", expid="{expid}")
    log: "log/{expid}-compute.log"
    wrapper: "file://esm_runscripts"

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
    log: "log/{expid}-tidy.log"
    wrapper: "file://esm_runscripts"

rule post:
    input: "results/{expid}_tidy.done"
    output: touch("results/{expid}_complete.done")
    params:
        runscript="config.yaml",
        task="post",
        expid="{expid}",
        reuse_config=True
    resources:
        **get_resources("config.yaml", "post", expid="{expid}")
    log: "log/{expid}-post.log"
    wrapper: "file://esm_runscripts"
```

## Simulation Phases

### prepcompute

Prepares the simulation environment:
- Creates directory structure
- Links input files
- Generates namelists
- Prepares restart files

```python
rule prepcompute:
    params:
        task="prepcompute",
        # ... other params
```

### compute

Executes the main model simulation:
- Runs coupled model components
- Writes output files
- Creates restart files

```python
rule compute:
    params:
        task="compute",
        # ... other params
```

### tidy

Post-run organization:
- Organizes output files
- Moves logs and diagnostics
- Prepares for archiving

```python
rule tidy:
    params:
        task="tidy",
        # ... other params
```

### post

Post-processing and analysis:
- Run analysis scripts
- Generate plots
- Create summaries

```python
rule post:
    params:
        task="post",
        # ... other params
```

## Resource Extraction

### Using get_resources()

The helper function automatically extracts resources:

```python
from esm_runscripts.helper import get_resources

resources:
    **get_resources("config.yaml", "compute", expid="exp001")
```

Returns:
```python
{
    'nodes': 4,
    'tasks': 288,
    'mem_mb': 204800,
    'runtime': 720,
    'partition': 'compute',
    'account': 'ab1234'
}
```

### How It Works

1. Runs `esm_runscripts --check`
2. Finds `{expid}_finished_config.yaml`
3. Parses configuration
4. Extracts resource specifications
5. Converts to Snakemake format

### Configuration Requirements

Your runscript must include:

```yaml
general:
  account: "ab1234"
  compute_time: "12:00:00"  # Converted to minutes
  cores: 288
  nodes: 4

computer:
  name: "levante"
  partition: "compute"
  memory_per_task: "200G"  # Converted to MB
```

## Advanced Usage

### Configuration Overrides

Apply runtime modifications:

```python
rule compute_modified:
    output: touch("results/exp_modified.done")
    params:
        runscript="base_config.yaml",
        task="compute",
        expid="exp_modified",
        modify_config="overrides.yaml"
    resources:
        **get_resources("base_config.yaml", "compute",
                       expid="exp_modified",
                       modify_config="overrides.yaml")
    wrapper: "file://esm_runscripts"
```

`overrides.yaml`:
```yaml
general:
  compute_time: "24:00:00"  # Extended runtime

awicm:
  resolution: "T63"  # Different resolution
```

### Custom Start Date

Resume from specific date:

```python
rule continue_simulation:
    params:
        runscript="config.yaml",
        task="compute",
        expid="exp001",
        current_date="2000-02-01",
        reuse_config=True
    resources:
        **get_resources("config.yaml", "compute", expid="exp001")
    wrapper: "file://esm_runscripts"
```

### Extra Arguments

Pass additional esm_runscripts flags:

```python
rule compute_verbose:
    params:
        runscript="config.yaml",
        task="compute",
        expid="exp001",
        extra="--verbose --debug"
    resources:
        **get_resources("config.yaml", "compute", expid="exp001")
    wrapper: "file://esm_runscripts"
```

## Provenance Tracking with herrkunft

The wrapper uses [herrkunft](https://pypi.org/project/herrkunft/) for YAML parsing, providing automatic provenance tracking:

### What is Tracked

- Original source file and line number
- Value modification history
- Inheritance chain through includes
- Configuration hierarchy

### Accessing Provenance

```python
import herrkunft as yaml

config = yaml.load(open("finished_config.yaml"))

# Values include provenance metadata
value = config['general']['compute_time']
# Tracks: where defined, how modified, inheritance path
```

### Benefits

- **Transparency**: Know exactly where values come from
- **Debugging**: Trace configuration issues quickly
- **Reproducibility**: Full configuration history
- **Documentation**: Auto-generated change logs

## Parameters Reference

### Required Parameters

**runscript** (str)
:   Path to ESM runscript YAML configuration

**task** (str)
:   Simulation phase: prepcompute, compute, tidy, post

### Optional Parameters

**expid** (str, default="test")
:   Experiment identifier

**reuse_config** (bool, default=False)
:   Skip config generation, reuse existing

**modify_config** (str, optional)
:   Path to configuration override file

**current_date** (str, optional)
:   Simulation start/restart date

**extra** (str, default="")
:   Additional esm_runscripts arguments

## Troubleshooting

### finished_config.yaml Not Found

**Symptom**: `FileNotFoundError: Could not find finished_config.yaml`

**Solution**:
1. Check experiment ID matches
2. Verify runscript is valid
3. Run `esm_runscripts --check` manually first

### Resource Extraction Fails

**Symptom**: `subprocess.CalledProcessError` from get_resources()

**Solution**:
1. Check esm_runscripts configuration
2. Verify required keys exist (compute_time, cores, etc.)
3. Run with verbose flag: `extra="--verbose"`

### Script Execution Fails

**Symptom**: Wrapper executes but simulation fails

**Solution**:
1. Check log file
2. Verify modules loaded correctly
3. Check working directory exists
4. Verify input files present

## Best Practices

### 1. Reuse Configuration

Only generate config once:

```python
rule prep:
    params:
        reuse_config=False  # Generate

rule compute:
    params:
        reuse_config=True  # Reuse
```

### 2. Chain Phases with Dependencies

Use Snakemake dependencies:

```python
rule compute:
    input: "results/{expid}_prep.done"
    # ...
```

### 3. Separate Experiments

Use wildcards for multiple experiments:

```python
rule all:
    input: expand("results/{exp}_done", exp=EXPERIMENTS)
```

### 4. Version Control Runscripts

Track runscripts in git:

```bash
git add *.yaml
git commit -m "Update model configuration"
```

## Related

- [API Reference](../api/esm_runscripts_wrapper.md)
- [Helper Module API](../api/esm_runscripts_helper.md)
- [Complete Workflow Guide](complete_workflow.md)
- [herrkunft Documentation](https://pypi.org/project/herrkunft/)

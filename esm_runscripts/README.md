# Snakemake Wrapper for esm_runscripts

Snakemake wrapper for `esm_runscripts` - the execution engine for Earth System Model (ESM) simulations. This wrapper enables Snakemake-based orchestration of ESM simulation workflows by intercepting batch submissions and executing within Snakemake's resource management framework.

## Overview

`esm_runscripts` is the core execution component of [esm-tools](https://github.com/esm-tools/esm_tools) that manages the complete lifecycle of ESM simulations. While `esm_master` handles model installation (downloading, configuring, compiling), `esm_runscripts` handles model execution (preparing, running, tidying).

This wrapper provides:
- **Snakemake orchestration**: Full DAG control over simulation phases
- **Resource management**: Automatic SLURM resource allocation via Snakemake
- **Granular execution**: Run individual phases or complete workflows
- **Environment handling**: Proper module loading and variable exports
- **Provenance tracking**: Integration with herrkunft for configuration tracking

## Architecture

### Two-Component System

The wrapper uses a sophisticated two-stage approach:

1. **Resource Extraction (Pre-DAG)**: `get_resources()` helper function
   - Runs `esm_runscripts --check` to generate configuration
   - Parses `finished_config.yaml` for resource requirements
   - Returns dict for Snakemake `resources:` declaration

2. **Execution (Runtime)**: `wrapper.py` script
   - Finds generated `.run` batch script
   - Extracts executable content (strips SLURM directives)
   - Executes within Snakemake's allocated resources

### Workflow Phases

`esm_runscripts` organizes simulations into distinct phases:

| Phase | Purpose | Typical Operations |
|-------|---------|-------------------|
| **prepcompute** | Prepare for computation | File staging, namelist generation, input linking |
| **compute** | Execute model | Run coupled ESM components |
| **tidy** | Post-run cleanup | Move outputs, update restart files, cleanup |
| **post** | Post-processing | Data analysis, visualization |

## Installation

### Requirements

- HPC environment with SLURM batch system
- esm-tools v6.59.2 or compatible
- Module system for software dependencies
- Snakemake with SLURM executor configured
- Python 3.10+

### Setup

The wrapper is installed as part of this repository:

```bash
git clone https://github.com/pgierz/snakemake-wrapper-esm-master.git
cd snakemake-wrapper-esm-master
```

## Usage

### Basic Usage

```python
from esm_runscripts_wrapper import get_resources

rule compute_phase:
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp001")
    wrapper:
        "file://path/to/esm_runscripts"
```

### Full Workflow Example

```python
from esm_runscripts_wrapper import get_resources

# Complete simulation workflow
rule all:
    input: "results/exp001_complete.done"

rule prepcompute:
    output: touch("results/exp001_prep.done")
    params:
        runscript="awicm.yaml",
        task="prepcompute",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "prepcompute", expid="exp001")
    log: "logs/exp001_prepcompute.log"
    wrapper: "file://esm_runscripts"

rule compute:
    input: "results/exp001_prep.done"
    output: touch("results/exp001_compute.done")
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp001")
    log: "logs/exp001_compute.log"
    wrapper: "file://esm_runscripts"

rule tidy:
    input: "results/exp001_compute.done"
    output: touch("results/exp001_complete.done")
    params:
        runscript="awicm.yaml",
        task="tidy",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "tidy", expid="exp001")
    log: "logs/exp001_tidy.log"
    wrapper: "file://esm_runscripts"
```

### With Configuration Override

```python
rule compute_modified:
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp002",
        modify_config="custom_settings.yaml"
    resources:
        **get_resources(
            "awicm.yaml",
            "compute",
            expid="exp002",
            modify_config="custom_settings.yaml"
        )
    wrapper: "file://esm_runscripts"
```

### Reusing Configuration

For subsequent runs or testing, you can reuse existing configuration:

```python
rule rerun_compute:
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp001",
        reuse_config=True  # Skip config regeneration
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp001")
    wrapper: "file://esm_runscripts"
```

### With Custom Start Date

```python
rule restart_from_date:
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp003",
        current_date="2000-01-01"  # Override start date
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp003")
    wrapper: "file://esm_runscripts"
```

## Parameters

### Required Parameters

- **runscript** (str): Path to ESM runscript YAML file
  - Example: `"awicm.yaml"`, `"configs/fesom_pi.yaml"`
  - This is the main configuration file defining your simulation setup

- **task** (str): Phase to execute
  - Options: `"prepcompute"`, `"compute"`, `"tidy"`, `"post"`
  - Determines which workflow phase runs

### Optional Parameters

- **expid** (str, default: `"test"`): Experiment ID
  - Used for directory naming and file identification
  - Example: `"exp001"`, `"PI-CTRL"`, `"historical-r1"`

- **reuse_config** (bool, default: `False`): Reuse existing finished_config.yaml
  - Set to `True` for subsequent runs to skip config generation
  - Useful for testing or re-running failed jobs

- **modify_config** (str, default: `None`): Path to config override file
  - Allows modification without editing main runscript
  - Example: `"production_overrides.yaml"`

- **current_date** (str, default: `None`): Override simulation start date
  - Format: `"YYYY-MM-DD"` (e.g., `"2000-01-01"`)
  - Useful for restart runs or date-specific tests

- **extra** (str, default: `""`): Additional command-line flags
  - Passed directly to `esm_runscripts`
  - Example: `"--verbose --debug"`

## Resource Extraction

The `get_resources()` helper automatically extracts:

| Resource | Description | Source in finished_config.yaml |
|----------|-------------|-------------------------------|
| **nodes** | Number of compute nodes | `general.resubmit_nodes` |
| **tasks** | Total MPI tasks | `general.resubmit_tasks` |
| **mem_mb** | Memory per task (MB) | `computer.memory_per_task` |
| **runtime** | Wall time (minutes) | `general.run_time` |
| **partition** | SLURM partition | `computer.partition` |
| **account** | SLURM account | `computer.account` |

### Example Resource Dictionary

```python
{
    'nodes': 10,
    'tasks': 240,
    'mem_mb': 180000,  # 180 GB
    'runtime': 720,     # 12 hours
    'partition': 'compute',
    'account': 'ab0123'
}
```

## How It Works

### Step-by-Step Execution

1. **Pre-DAG (get_resources)**:
   ```bash
   esm_runscripts --check <runscript> -t <task> -e <expid>
   ```
   - Generates `finished_config.yaml` with all resolved settings
   - Generates `.run` batch script (not submitted)
   - Returns resource dict for Snakemake

2. **DAG Building**:
   - Snakemake parses resources for each rule
   - Builds execution DAG with dependencies
   - Allocates SLURM resources

3. **Runtime (wrapper.py)**:
   - Locates generated `.run` script
   - Parses script, extracting:
     - Module load commands
     - Environment exports
     - Working directory changes
     - Execution commands
   - Strips SLURM directives (`#SBATCH`)
   - Executes content in Snakemake's allocated resources

### File Locations

```
{expid}/
├── config/
│   └── {expid}_finished_config.yaml    # Resolved configuration
├── scripts/
│   ├── {expid}_{cluster}_{date}.run    # Generated batch script
│   └── {expid}_{cluster}_{date}_snakemake.sh  # Temporary execution script
├── work/                                # Working directory
├── outdata/                             # Model outputs
└── restart/                             # Restart files
```

## Environment Handling

The wrapper properly handles environment setup from esm_runscripts:

### Module Loads

From `finished_config.yaml`:
```yaml
computer:
  module_actions:
    - load echam/6.3.05p2
    - load fesom/2.0
    - load oasis/3.0
```

Translated to:
```bash
module load echam/6.3.05p2
module load fesom/2.0
module load oasis/3.0
```

### Environment Exports

From `finished_config.yaml`:
```yaml
computer:
  environment_changes:
    add_export_vars:
      OMP_NUM_THREADS: 4
      KMP_AFFINITY: "compact"
      FESOM_USE_CACHING: 1
```

Translated to:
```bash
export OMP_NUM_THREADS=4
export KMP_AFFINITY=compact
export FESOM_USE_CACHING=1
```

## Comparison with Direct esm_runscripts Usage

| Aspect | Direct esm_runscripts | Snakemake Wrapper |
|--------|----------------------|-------------------|
| **Orchestration** | Manual phase sequencing | Automatic DAG-based |
| **Resource Management** | SLURM direct submission | Snakemake SLURM executor |
| **Parallelization** | Limited to model internals | Multi-job parallel execution |
| **Dependency Tracking** | Manual | Automatic file-based |
| **Reproducibility** | Good (esm-tools) | Excellent (+ Snakemake) |
| **Workflow Composition** | Sequential scripts | Flexible DAG |
| **Multi-Experiment** | Serial execution | Parallel execution |

## Advanced Usage

### Multiple Experiments in Parallel

```python
EXPIDS = ["exp001", "exp002", "exp003"]

rule all:
    input:
        expand("results/{expid}_complete.done", expid=EXPIDS)

rule compute_experiment:
    output: touch("results/{expid}_complete.done")
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="{expid}"
    resources:
        **lambda wildcards: get_resources(
            "awicm.yaml",
            "compute",
            expid=wildcards.expid
        )
    wrapper: "file://esm_runscripts"
```

### Conditional Phases

```python
rule compute_with_optional_post:
    input:
        compute="results/{expid}_compute.done",
        post="results/{expid}_post.done" if DO_POSTPROCESSING else []
    output: touch("results/{expid}_complete.done")
```

### Integration with Data Processing

```python
rule process_output:
    input: "results/{expid}_tidy.done"
    output: "results/{expid}_processed.nc"
    shell:
        "cdo -O -f nc4 copy {expid}/outdata/output.nc {output}"

rule plot_results:
    input: "results/{expid}_processed.nc"
    output: "figures/{expid}_plot.png"
    script: "scripts/plot_results.py"
```

## Troubleshooting

### Config Generation Fails

**Symptom**: `esm_runscripts --check` fails

**Solutions**:
- Verify runscript path is correct and accessible
- Check that esm_runscripts is in PATH: `which esm_runscripts`
- Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('runscript.yaml'))"`
- Check esm-tools version: `pip show esm-tools`

### Run Script Not Found

**Symptom**: `FileNotFoundError: Could not find .run script`

**Solutions**:
- Ensure `--check` mode completed successfully
- Verify scripts directory exists: `ls {expid}/scripts/`
- Check expid matches between config generation and execution
- Look for error messages in generation step

### Module Loads Fail

**Symptom**: `module: command not found` or module load errors

**Solutions**:
- Confirm module system available: `module avail`
- Check module names in runscript match system: `module avail <name>`
- Verify compute nodes have module system (not just login nodes)
- Check module environment in SLURM: add `module list` to verify

### Resource Mismatch

**Symptom**: Job fails with resource errors or doesn't start

**Solutions**:
- Ensure `get_resources()` uses **same parameters** as wrapper
- Verify `finished_config.yaml` is up-to-date (not from old run)
- Check SLURM limits: `sinfo -o "%P %l %D"` for partition limits
- Validate memory format in config (GB vs MB)

### Execution Fails

**Symptom**: Wrapper executes but model fails

**Solutions**:
- Check log files in `logs/` directory
- Verify input files exist: `ls {expid}/input/`
- Check model-specific logs: `{expid}/outdata/`
- Review esm_runscripts documentation for model setup

## Testing

Run the test suite:

```bash
cd esm_runscripts/test
snakemake --cores 1 --use-conda
```

This tests:
- Single phase execution
- Full workflow with dependencies
- Configuration override
- Config reuse

## Limitations

- **HPC-only**: Requires SLURM batch system
- **esm-tools dependency**: Wrapper tightly coupled to esm_runscripts behavior
- **File-based coordination**: Uses touch files for dependencies
- **No streaming**: Cannot monitor running jobs (use esm_runscripts observe)

## Related Tools

- [esm_master wrapper](../esm_master/): For model installation
- [esm-tools](https://github.com/esm-tools/esm_tools): Core ESM workflow tools
- [herrkunft](https://github.com/pgierz/herrkunft): Configuration provenance tracking

## Contributing

Contributions welcome! Please:
1. Test with your specific ESM setup
2. Report issues with runscript examples
3. Suggest improvements for resource handling
4. Share advanced workflow patterns

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Authors

- **Paul Gierz** - paul.gierz@awi.de

## Citation

If you use this wrapper in your research, please cite:

```bibtex
@software{snakemake_esm_runscripts,
  title = {Snakemake Wrapper for esm\_runscripts},
  author = {Gierz, Paul},
  year = {2025},
  url = {https://github.com/pgierz/snakemake-wrapper-esm-master}
}
```

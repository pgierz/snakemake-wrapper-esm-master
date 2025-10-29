# esm_runscripts Helper Module API

This page documents the helper module for extracting Snakemake resources from esm_runscripts configuration.

## Module Documentation

```{eval-rst}
.. automodule:: esm_runscripts.helper
   :members:
   :undoc-members:
   :show-inheritance:
```

## Main Function

### get_resources

```{eval-rst}
.. autofunction:: esm_runscripts.helper.get_resources
```

## Usage

The helper module is designed to be imported and used in Snakefiles to automatically determine resource requirements:

```python
from esm_runscripts.helper import get_resources

rule compute_phase:
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp001")
    wrapper:
        "file://esm_runscripts"
```

## Function Details

### get_resources()

Extract Snakemake resources by running `esm_runscripts --check`.

**Parameters:**
- `runscript` (str): Path to ESM runscript YAML file
- `task` (str): Phase to execute (prepcompute/compute/tidy/post)
- `expid` (str): Experiment ID (default: "test")
- `modify_config` (str, optional): Path to config override file
- `base_dir` (str, optional): Base directory for experiment (default: current dir)
- `**extra_args`: Additional arguments passed to esm_runscripts

**Returns:**
- Dictionary with Snakemake resource specifications:
  - `nodes`: Number of compute nodes
  - `tasks`: Number of tasks/cores
  - `mem_mb`: Memory in megabytes
  - `runtime`: Runtime in minutes
  - `partition`: SLURM partition name (if specified)
  - `account`: SLURM account (if specified)

**Raises:**
- `FileNotFoundError`: If runscript doesn't exist
- `subprocess.CalledProcessError`: If esm_runscripts --check fails
- `ValueError`: If finished_config.yaml cannot be parsed

**Example:**

```python
resources = get_resources(
    "awicm.yaml",
    "compute",
    expid="exp001",
    modify_config="overrides.yaml"
)
# Returns:
# {
#     'nodes': 4,
#     'tasks': 288,
#     'mem_mb': 204800,
#     'runtime': 720,
#     'partition': 'compute',
#     'account': 'ab1234'
# }
```

## Wrapper Execution Functions

These functions handle the actual execution of esm_runscripts within Snakemake:

### find_run_script

```{eval-rst}
.. autofunction:: esm_runscripts.helper.find_run_script
```

### extract_executable_content

```{eval-rst}
.. autofunction:: esm_runscripts.helper.extract_executable_content
```

### write_executable_script

```{eval-rst}
.. autofunction:: esm_runscripts.helper.write_executable_script
```

## Internal Functions

These functions are used internally by `get_resources()`:

### _find_finished_config

```{eval-rst}
.. autofunction:: esm_runscripts.helper._find_finished_config
```

### _extract_resources_from_config

```{eval-rst}
.. autofunction:: esm_runscripts.helper._extract_resources_from_config
```

### _parse_memory

```{eval-rst}
.. autofunction:: esm_runscripts.helper._parse_memory
```

### _parse_time

```{eval-rst}
.. autofunction:: esm_runscripts.helper._parse_time
```

## Advanced Usage

### Custom Base Directory

```python
resources = get_resources(
    "config.yaml",
    "compute",
    expid="exp001",
    base_dir="/path/to/experiments"
)
```

### Extra esm_runscripts Arguments

```python
resources = get_resources(
    "config.yaml",
    "compute",
    expid="exp001",
    verbose=True,  # Passed as --verbose
    check_coupling=True  # Passed as --check-coupling
)
```

### Error Handling

```python
try:
    resources = get_resources("config.yaml", "compute", expid="exp001")
except FileNotFoundError as e:
    print(f"Config file not found: {e}")
except subprocess.CalledProcessError as e:
    print(f"esm_runscripts failed: {e.stderr}")
except ValueError as e:
    print(f"Config parsing error: {e}")
```

## Integration with herrkunft

The helper module attempts to use [herrkunft](https://pypi.org/project/herrkunft/) for YAML parsing when available, falling back to PyYAML otherwise:

```python
try:
    import herrkunft as yaml
except ImportError:
    import yaml
```

Using herrkunft provides automatic provenance tracking for all configuration values.

## Related

- [esm_runscripts Wrapper API](esm_runscripts_wrapper.md)
- [esm_runscripts Usage Guide](../guides/esm_runscripts_usage.md)
- [herrkunft Documentation](https://pypi.org/project/herrkunft/)

# Snakemake Wrappers for ESM-Tools

Welcome to the documentation for Snakemake wrappers that integrate [esm-tools](https://github.com/esm-tools/esm_tools) into reproducible scientific workflows.

## Overview

This package provides two complementary Snakemake wrappers for managing Earth System Models:

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} esm_master
:link: guides/esm_master_usage
:link-type: doc

Model installation wrapper for downloading, configuring, and compiling Earth System Models.

**Key Features:**
- Download source code from repositories
- Configure models for compilation
- Compile model binaries
- Support for all esm_master subcommands
:::

:::{grid-item-card} esm_runscripts
:link: guides/esm_runscripts_usage
:link-type: doc

Model execution wrapper for running Earth System Model simulations within Snakemake.

**Key Features:**
- Automatic resource extraction
- YAML provenance tracking with herrkunft
- Support for all simulation phases
- Seamless Snakemake integration
:::

::::

## Why Use These Wrappers?

### Reproducibility
- Version-controlled workflows using Snakemake
- Automatic dependency tracking
- Consistent execution across different systems

### Resource Management
- Automatic SLURM resource detection
- Integration with Snakemake's resource management
- No manual resource specification needed

### Provenance Tracking
- Configuration changes tracked through herrkunft library
- Full history of parameter modifications
- Transparent YAML processing

### Simplified Workflows
- Combine model installation and execution
- Standard Snakemake patterns and best practices
- Easy integration with existing pipelines

## Quick Start

### Installation

```python
# In your Snakefile
rule install_model:
    output: touch("models/awicm-3.0/.installed")
    params:
        model="awicm",
        version="3.0"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

### Running Simulations

```python
from esm_runscripts.helper import get_resources

rule run_simulation:
    input: "models/awicm-3.0/.installed"
    output: touch("results/exp001_complete.done")
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp001")
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"
```

## Documentation Contents

```{toctree}
:maxdepth: 2
:caption: Contents

guides/installation
guides/quickstart
guides/esm_master_usage
guides/esm_runscripts_usage
guides/complete_workflow
api/esm_master_wrapper
api/esm_runscripts_wrapper
api/esm_runscripts_helper
examples/basic_install
examples/simulation_workflow
examples/advanced_usage
```

## Support

- **GitHub Issues:** [Report bugs or request features](https://github.com/pgierz/snakemake-wrapper-esm-master/issues)
- **esm-tools Documentation:** [https://esm-tools.readthedocs.io](https://esm-tools.readthedocs.io)
- **Snakemake Documentation:** [https://snakemake.readthedocs.io](https://snakemake.readthedocs.io)

## License

MIT License - Copyright (c) 2025 Paul Gierz

## Citation

If you use these wrappers in your research, please cite:

```bibtex
@software{gierz2025snakemake_esm,
  author = {Gierz, Paul},
  title = {Snakemake Wrappers for ESM-Tools},
  year = {2025},
  url = {https://github.com/pgierz/snakemake-wrapper-esm-master}
}
```

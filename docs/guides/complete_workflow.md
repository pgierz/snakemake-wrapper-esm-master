# Complete Workflow Example

This guide demonstrates a full end-to-end workflow combining model installation and execution.

## Full Workflow Snakefile

```python
from esm_runscripts.helper import get_resources

# Configuration
MODELS = {"awicm": "3.0"}
EXPERIMENTS = ["control", "perturbation"]

# Target: all experiments completed
rule all:
    input:
        expand("results/{exp}_complete.done", exp=EXPERIMENTS)

# Step 1: Install model (once)
rule install_model:
    output:
        touch("models/{model}-{version}/.installed")
    params:
        model="{model}",
        version="{version}"
    log:
        "log/install_{model}-{version}.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"

# Step 2-5: Run complete simulation workflow for each experiment
rule prepcompute:
    input:
        lambda w: expand("models/{model}-{version}/.installed",
                        zip, model=MODELS.keys(), version=MODELS.values())
    output:
        touch("results/{exp}_prep.done")
    params:
        runscript="configs/{exp}.yaml",
        task="prepcompute",
        expid="{exp}"
    resources:
        **get_resources("configs/{exp}.yaml", "prepcompute", expid="{exp}")
    log:
        "log/{exp}_prep.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"

rule compute:
    input:
        "results/{exp}_prep.done"
    output:
        touch("results/{exp}_compute.done")
    params:
        runscript="configs/{exp}.yaml",
        task="compute",
        expid="{exp}",
        reuse_config=True
    resources:
        **get_resources("configs/{exp}.yaml", "compute", expid="{exp}")
    log:
        "log/{exp}_compute.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"

rule tidy:
    input:
        "results/{exp}_compute.done"
    output:
        touch("results/{exp}_tidy.done")
    params:
        runscript="configs/{exp}.yaml",
        task="tidy",
        expid="{exp}",
        reuse_config=True
    resources:
        **get_resources("configs/{exp}.yaml", "tidy", expid="{exp}")
    log:
        "log/{exp}_tidy.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"

rule post:
    input:
        "results/{exp}_tidy.done"
    output:
        touch("results/{exp}_complete.done")
    params:
        runscript="configs/{exp}.yaml",
        task="post",
        expid="{exp}",
        reuse_config=True
    resources:
        **get_resources("configs/{exp}.yaml", "post", expid="{exp}")
    log:
        "log/{exp}_post.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"
```

## Directory Structure

```
project/
├── Snakefile
├── configs/
│   ├── control.yaml
│   └── perturbation.yaml
├── models/
│   └── awicm-3.0/
│       └── .installed
├── results/
│   ├── control_complete.done
│   └── perturbation_complete.done
└── log/
    ├── install_awicm-3.0.log
    ├── control_prep.log
    ├── control_compute.log
    └── ...
```

## Running the Workflow

```bash
# Dry run
snakemake -n

# Execute
snakemake --use-conda -c8

# Or on HPC with cluster profile
snakemake --profile slurm -c100
```

See the [examples](../examples/) directory for more complete workflows.

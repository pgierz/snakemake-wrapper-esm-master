# Example: Advanced Usage

Advanced patterns for complex workflows.

## Multiple Experiments with Wildcards

```python
from esm_runscripts.helper import get_resources

EXPERIMENTS = ["control", "2xCO2", "4xCO2"]

rule all:
    input:
        expand("results/{exp}_done.txt", exp=EXPERIMENTS)

rule run_experiment:
    output:
        touch("results/{exp}_done.txt")
    params:
        runscript="configs/{exp}.yaml",
        task="compute",
        expid="{exp}"
    resources:
        **get_resources("configs/{exp}.yaml", "compute", expid="{exp}")
    log:
        "log/{exp}.log"
    wrapper:
        "file://esm_runscripts"
```

## Configuration Overrides

```python
rule perturbed_run:
    output: touch("results/perturbed_done.txt")
    params:
        runscript="base.yaml",
        task="compute",
        expid="perturbed",
        modify_config="perturbation.yaml"
    resources:
        **get_resources("base.yaml", "compute",
                       expid="perturbed",
                       modify_config="perturbation.yaml")
    wrapper: "file://esm_runscripts"
```

## Staged Installation

```python
rule download:
    output: touch("models/{model}-{version}/.downloaded")
    params:
        subcommand="get",
        model="{model}",
        version="{version}"
    wrapper: "file://esm_master"

rule compile:
    input: "models/{model}-{version}/.downloaded"
    output: touch("models/{model}-{version}/.compiled")
    params:
        subcommand="comp",
        model="{model}",
        version="{version}"
    wrapper: "file://esm_master"
```

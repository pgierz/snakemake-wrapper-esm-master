# Example: Complete Simulation Workflow

Example showing installation and simulation execution.

## Snakefile

```python
from esm_runscripts.helper import get_resources

rule all:
    input: "results/exp001_complete.done"

rule install:
    output: touch("models/awicm-3.0/.installed")
    params:
        model="awicm",
        version="3.0"
    log: "log/install.log"
    wrapper: "file://esm_master"

rule compute:
    input: "models/awicm-3.0/.installed"
    output: touch("results/exp001_complete.done")
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp001")
    log: "log/compute.log"
    wrapper: "file://esm_runscripts"
```

See [Complete Workflow Guide](../guides/complete_workflow.md) for more details.

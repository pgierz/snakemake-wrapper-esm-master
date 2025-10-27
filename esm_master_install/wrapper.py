__author__ = "Paul Gierz"
__copyright__ = "Copyright 2025, Paul Gierz"
__email__ = "paul.gierz@awi.de"
__license__ = "MIT"

from snakemake.shell import shell

log = snakemake.log_fmt_shell(stdout=True, stderr=True)

model_name = snakemake.params.get("model")
model_version = snakemake.params.get("version")
extra = snakemake.params.get("extra", "")

shell(
    "esm-master install-{model_name}-{model_version}"
    " {extra}"
    " {log}"
)

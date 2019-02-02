from snakemake.utils import validate
from snakemake.utils import min_version
import pandas as pd

__author__ = 'Kuan-Hao Chao <b05901180@ntu.edu.tw>'

#------------ Depend on a min_version ---------

#------------ Config setup ------------
configfile: "config.yaml"
validate(config, "schemas/config.schema.yaml")
print("Hi")


# Tabular configuration
# samples = pd.read_table(config["samples"]).set_index("sample", drop=FALSE)
# validate(samples, schema="schemas/cells.schema.yaml")

#------------ Definition fo all_input ------
all_input = [
    "a",
    "b",
]

#------------ Target File -------------
rule all:
    input:
        f2=expand(os.path.join(config["root_dir"],"analysis_results", "{filename}.upper.down.txt"), filename=all_input)
    #input: all_input
    #shell:
    #    "echo \"Evreything is done! \""


#------------ include rules -----------
include: "./rules/trimmomatic_trimming_PE.snakefile"
include: "./rules/bwa_alignment.snakefile"


#------------ setup report ------------

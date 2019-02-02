from snakemake.utils import validate
from snakemake.utils import min_version
import pandas as pd

__author__ = 'Kuan-Hao Chao <b05901180@ntu.edu.tw>'

#------------ Depend on a min_version ---------

#------------ Config setup ------------
configfile: "config.yaml"
validate(config, "schemas/config.schema.yaml")
# pipesDir = os.path.join(os.path.expanduser(config['bin_dir']), 'pipes', 'rules')


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
        f2=expand(os.path.join(config["result_data"], "{filename}.upper.down.txt"), filename=all_input)
    #input: all_input
    #shell:
    #    "echo \"Evreything is done! \""

rule trim:
    input:
        r1=os.path.join(config["ref_data"], "{sample}.1.fastq.gz"),
        r2=os.path.join(config["ref_data"], "{sample}.2.fastq.gz")
    output:
        r1=os.path.join(config["result_data"], "{sample}.1.fastq.gz"),
        r2=os.path.join(config["result_data"], "{sample}.2.fastq.gz"),
        # reads where trimming entirely removed the mate
        r1_unpaired=os.path.join(config["result_data"], "{sample}.1.unpaired.fastq.gz"),
        r2_unpaired=os.path.join(config["result_data"], "{sample}.2.unpaired.fastq.gz")
    log:
        os.path.join(config["result_data"], "logs/trimmomatic/{sample}.log")
    params:
        # list of trimmers (see manual)
        trimmer=["TRAILING:3"],
        # optional parameters
        extra="",
        compression_level="-9"
    wrapper:
        "0.31.1/bio/trimmomatic/pe"

#------------ include rules -----------
# include: "./rules/trimmomatic_trimming_PE.snakefile"
# include: "./rules/bwa_alignment.snakefile"


#------------ setup report ------------

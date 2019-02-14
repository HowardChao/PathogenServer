from snakemake.utils import validate
from snakemake.utils import min_version
import os
import pandas as pd

__author__ = 'Kuan-Hao Chao <b05901180@ntu.edu.tw>'

#------------ Depend on a min_version ---------

#------------ Config setup ------------
configfile: "config.yaml"
print(os.path.join(config["datadir"], config["project_name"], config["se_or_pe"]))
workdir: os.path.join(config["datadir"], config["project_name"], config["se_or_pe"])
trimmomatic_jar = config["trimmomatic_jar"]
validate(config, "schemas/config.schema.yaml")
# pipesDir = os.path.join(os.path.expanduser(config['bin_dir']), 'pipes', 'rules')


# Tabular configuration
# samples = pd.read_table(config["samples"]).set_index("sample", drop=FALSE)
# validate(samples, schema="schemas/cells.schema.yaml")

#------------ Definition fo all_input ------
samples = {os.path.splitext(os.path.splitext(f)[0])[0] for f in os.listdir(".") if f.endswith(".fastq")}
print(samples)

#------------ Target File -------------
# rule all:
#     input:
#         f2=expand(os.path.join(config["result_data"], "{filename}.upper.down.txt"), filename=all_input)
    #input: all_input
    #shell:
    #    "echo \"Evreything is done! \""

rule targets:
    input:
        expand("{sample}_r1_paired.fastq.gz", sample=samples)

rule preprocess:
    input:
        r1 = "{sample}.R1.fastq",
        r2 = "{sample}.R2.fastq",
    output:
        r1_paired = "{sample}_r1_paired.fastq.gz",
        r1_unpaired = "{sample}_r1_unpaired.fastq.gz",
        r2_paired = "{sample}_r2_paired.fastq.gz",
        r2_unpaired = "{sample}_r2_unpaired.fastq.gz"
    message: "Trimming Illumina adapters from {input.r1} and {input.r2}"
    shell:
        """
        java -jar config[trimmomatic_jar] PE {input.r1} {input.r2} {output.r1_paired} \
        {output.r1_unpaired} {output.r2_paired} {output.r2_unpaired} \
        ILLUMINACLIP:{config[adapter]} LEADING:{config[leading]} TRAILING:{config[trailing]} SLIDINGWINDOW:{config[window]} MINLEN:{config[minlen]}
        """
#
# rule trimmomatic_pe:
#     input:
#         r1=os.path.join(os.path.expanduser(config["ref_data"]), "ip96_S13.1.fastq.gz"),
#         r2=os.path.join(os.path.expanduser(config["ref_data"]), "ip96_S13.2.fastq.gz")
#     output:
#         r1="trimmed/ip96_S13.1.fastq.gz",
#         r2="trimmed/ip96_S13.2.fastq.gz",
#         # reads where trimming entirely removed the mate
#         r1_unpaired="trimmed/ip96_S13.1.unpaired.fastq.gz",
#         r2_unpaired="trimmed/ip96_S13.2.unpaired.fastq.gz"
#     log:
#         "logs/trimmomatic/ip96_S13.log"
#     params:
#         # list of trimmers (see manual)
#         trimmer=["TRAILING:3"],
#         # optional parameters
#         extra="",
#         compression_level="-9"
#     wrapper:
#         "0.31.1/bio/trimmomatic/pe"


# print(os.path.join(os.path.expanduser(config["ref_data"]), "{sample}.1.fastq.gz"))
# rule trim:
#     input:
#         r1=os.path.join(os.path.expanduser(config["ref_data"]), "{sample}.1.fastq.gz"),
#         r2=os.path.join(os.path.expanduser(config["ref_data"]), "{sample}.2.fastq.gz")
#     output:
#         r1=os.path.join(os.path.expanduser(config["result_data"]), "{sample}.1.fastq.gz"),
#         r2=os.path.join(os.path.expanduser(config["result_data"]), "{sample}.2.fastq.gz"),
#         # reads where trimming entirely removed the mate
#         r1_unpaired=os.path.join(os.path.expanduser(config["result_data"]), "{sample}.1.unpaired.fastq.gz"),
#         r2_unpaired=os.path.join(os.path.expanduser(config["result_data"]), "{sample}.2.unpaired.fastq.gz")
#     log:
#         os.path.join(os.path.expanduser(config["result_data"]), "logs/trimmomatic/{sample}.log")
#     params:
#         # list of trimmers (see manual)
#         trimmer=["TRAILING:3"],
#         # optional parameters
#         extra="",
#         compression_level="-9"
#     wrapper:
#         "0.31.1/bio/trimmomatic/pe"

#------------ include rules -----------
# include: "./rules/trimmomatic_trimming_PE.snakefile"
# include: "./rules/bwa_alignment.snakefile"


#------------ setup report ------------

print(os.path.join(config["root_dir"], "virus_data", "{filename}.txt"))
import os
rule trimmomatic_trimming_PE:
    input:
        f1=os.path.join(config["result_data"], "{filename}.txt")
    output:
        f2=os.path.join(config["result_data"], "{filename}.upper.txt")
    shell:
        "echo tr [a-z] [A-Z] < {input.f1} > {output.f2}"

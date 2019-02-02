import os
rule bwa_alignment:
    input:
        f1=os.path.join(config["result_data"], "{filename}.upper.txt")
    output:
        f2=os.path.join(config["result_data"], "{filename}.upper.down.txt")
    shell:
        "tr [A-Z] [a-z] < {input.f1} > {output.f2}"

import os
rule bwa_alignment:
    input:
        f1=os.path.join(config["root_dir"], "analysis_results", "{filename}.upper.txt")
    output:
        f2=os.path.join(config["root_dir"], "analysis_results", "{filename}.upper.down.txt")
    shell:
        "tr [A-Z] [a-z] < {input.f1} > {output.f2}"

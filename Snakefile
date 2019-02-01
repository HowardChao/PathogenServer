from snakemake.utils import validate
from snakemake.utils import min_version
import pandas as pd

__author__ = 'Kuan-Hao Chao <b05901180@ntu.edu.tw>'

#------------ Depend on a min_version ---------
# min_version(3.2)

#------------ Config setup ------------
configfile: "config.yaml"
validate(config, "schemas/config.schema.yaml")
print("Hi")


# Tabular configuration
# samples = pd.read_table(config["samples"]).set_index("sample", drop=FALSE)
# validate(samples, schema="schemas/cells.schema.yaml")

#------------ Target File -------------
# rule all:
#     input:



#------------ include rules -----------




#------------ setup report ------------

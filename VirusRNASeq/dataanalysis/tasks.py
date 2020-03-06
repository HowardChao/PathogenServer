from __future__ import absolute_import, unicode_literals
from celery import shared_task
import subprocess
import os
import delegator

@shared_task
def start_snakemake_task(working_directory):
    print("Start snakemake")
    print("working_directory: ", working_directory)
    print("Print finished !!")


    snakefile = os.path.join(working_directory, 'Snakefile')
    print("snakefile!! : ", snakefile)
    # subprocess.check_output(['/ssd/Howard/Virus/venv/bin/snakemake', '-s', snakefile], shell=True)
    # os.system('/ssd/Howard/Virus/venv/bin/snakemake -s ' + snakefile)

    snakemake_command = '/ssd/Howard/Virus/venv/bin/snakemake' + snakefile
    snakemake_result = delegator.run('whoami', block=False)
    print("c.pid: ", snakemake_result.pid)
    print("c.out: whoami ~ ", snakemake_result.out)
    print("c.return_code: ", snakemake_result.return_code)

    snakemake_result = delegator.run('groups', block=False)
    print("c.pid: ", snakemake_result.pid)
    print("c.out: groups ~ ", snakemake_result.out)
    print("c.return_code: ", snakemake_result.return_code)
    print("Second time!")

    # snakemake_command = '/ssd/Howard/Virus/venv/bin/snakemake' + snakefile
    # snakemake_result = delegator.run('/ssd/Howard/Virus/venv/bin/snakemake', cwd = working_directory, block=False)
    # print("c.pid: ", snakemake_result.pid)
    # print("c.out: ", snakemake_result.out)
    # print("c.return_code: ", snakemake_result.return_code)
    snakemake_output_file = os.path.join(working_directory, 'logs', 'snakemake_output.log')
    snakemake_result = subprocess.call(['/ssd/Howard/Virus/venv/bin/snakemake'], cwd=working_directory, shell=True)
    # Write snakemake output to log file!
    # print("snakemake_result: ", snakemake_result)
    # with open('snakemake_output_file', 'wb') as f:
    #     f.write(snakemake_output_file.stdout)

    print("snakemake_result: ", snakemake_result)

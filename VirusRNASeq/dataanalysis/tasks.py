from __future__ import absolute_import, unicode_literals
from celery import shared_task
import subprocess

@shared_task
def start_snakemake_task(working_directory):
    print("Inside 'start_snakemake_task' !!!!!!")
    snakemake_result = subprocess.call(['snakemake'], cwd = working_directory)
    # django_q_tasks.async_task(subprocess.call, ['snakemake'], cwd=base_dir, q_options=opts)
    return snakemake_result

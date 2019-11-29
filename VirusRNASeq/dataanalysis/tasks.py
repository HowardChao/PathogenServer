from __future__ import absolute_import, unicode_literals
from celery import shared_task

@shared_task
def start_snakemake_task(x, y):
    print("Inside 'start_snakemake_task' !!!!!!")
    return x + y

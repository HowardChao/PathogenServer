import os
from django.conf import settings


def check_first_qc(datadir, sample_name, se_or_pe):
    root_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', datadir, 'QC', 'pre')
    if se_or_pe == 'pe':
        print("**** Inside check_first_qc function:")
        print("R1 html: ", os.path.join(root_dir, sample_name+".R1_fastqc.html"))
        print("R2 html: ", os.path.join(root_dir, sample_name+".R2_fastqc.html"))
        print("R1 zip: ", os.path.join(root_dir, sample_name+".R1_fastqc.zip"))
        print("R2 zip: ", os.path.join(root_dir, sample_name+".R2_fastqc.zip"))
        print("multiqc html: ", os.path.join(root_dir, sample_name+"_multiqc.html"))
        print("multiqc dir: ", os.path.join(
            root_dir, sample_name+"_multiqc_data"))
        r1_html = os.path.exists(os.path.join(root_dir, sample_name+".R1_fastqc.html"))
        r2_html = os.path.exists(os.path.join(root_dir, sample_name+".R2_fastqc.html"))
        r1_zip = os.path.exists(os.path.join(root_dir, sample_name+".R1_fastqc.zip"))
        r2_zip = os.path.exists(os.path.join(root_dir, sample_name+".R2_fastqc.zip"))
        multiqc_html = os.path.exists(os.path.join(root_dir, sample_name+"_multiqc.html"))
        multiqc_dir = os.path.exists(os.path.join(root_dir, sample_name+"_multiqc_data"))
        print("r1_html: ", r1_html)
        print("r2_html: ", r2_html)
        print("r1_zip: ", r1_zip)
        print("r2_zip: ", r2_zip)
        print("multiqc_html: ", multiqc_html)
        print("multiqc_dir: ", multiqc_dir)
        if r1_html and r2_html and r1_zip and r2_zip and multiqc_html and multiqc_dir:
            return True
        else:
            return False
    elif se_or_pe == 'se':
        # Will be added in the future
        return True


def check_trimming_qc(datadir, sample_name, se_or_pe):
    root_dir_trimmed_paired = os.path.join(settings.MEDIA_ROOT, 'tmp', datadir, "trimmed_paired")
    root_dir_trimmed_unpaired = os.path.join(
        settings.MEDIA_ROOT, 'tmp', datadir, "trimmed_unpaired")
    if se_or_pe == 'pe':
        print("**** Inside trimmomatic_pe_target function:")
        print("r1_paired: ", os.path.join(
            root_dir_trimmed_paired, sample_name+"_r1_paired.fastq.gz"))
        print("r2_paired: ", os.path.join(
            root_dir_trimmed_paired, sample_name+"_r2_paired.fastq.gz"))
        print("r1_unpaired: ", os.path.join(
            root_dir_trimmed_unpaired, sample_name+"_r1_unpaired.fastq.gz"))
        print("r2_unpaired: ", os.path.join(
            root_dir_trimmed_unpaired, sample_name+"_r2_unpaired.fastq.gz"))
        r1_paired = os.path.exists(os.path.join(
            root_dir_trimmed_paired, sample_name+"_r1_paired.fastq.gz"))
        r2_paired = os.path.exists(os.path.join(
            root_dir_trimmed_paired, sample_name+"_r2_paired.fastq.gz"))
        r1_unpaired = os.path.exists(os.path.join(
            root_dir_trimmed_unpaired, sample_name+"_r1_unpaired.fastq.gz"))
        r2_unpaired = os.path.exists(os.path.join(
            root_dir_trimmed_unpaired, sample_name+"_r2_unpaired.fastq.gz"))
        print("r1_paired: ", r1_paired)
        print("r2_paired: ", r2_paired)
        print("r1_unpaired: ", r1_unpaired)
        print("r2_unpaired: ", r2_unpaired)
        if r1_paired and r2_paired and r1_unpaired and r2_unpaired:
            return True
        else:
            return False
    elif se_or_pe == 'se':
        # Will be added in the future
        return True


def check_second_qc(datadir, sample_name, se_or_pe):
    return False
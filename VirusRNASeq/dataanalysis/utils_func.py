import os
import csv
import pandas
from django.conf import settings
from . import tasks

#################
### File URLs ###
#################
def get_sample_file_url(project_name, email, analysis_code):
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    url_base_dir = os.path.join('/media', 'tmp', project_name + '_' + email + '_' + analysis_code)
    samples_csv_file = os.path.join(base_dir, "samples.csv")
    if os.path.exists(samples_csv_file):
        uploaded_sample_file_url = os.path.join(url_base_dir, "samples.csv")
        return uploaded_sample_file_url
    else:
        return "#"

#####################
### Time function ###
#####################
def get_submission_time(project_name, email, analysis_code):
    submission_time_strip = 'no submission time'
    submission_time_file = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                        project_name + '_' + email + '_' + analysis_code, 'time/submision_time.txt')
    if os.path.exists(submission_time_file):
        f_submission = open(submission_time_file, "r")
        submission_time_strip = f_submission.read()
    return submission_time_strip

def get_start_time(project_name, email, analysis_code):
    start_time_strip = 'no start time'
    start_time_file = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                   project_name + '_' + email + '_' + analysis_code, 'time/start_time.txt')
    if os.path.exists(start_time_file):
        f_start = open(start_time_file, "r")
        start_time_strip = f_start.read()
    return start_time_strip

def get_end_time(project_name, email, analysis_code):
    end_time_strip = 'no end time'
    end_time_file = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                   project_name + '_' + email + '_' + analysis_code, 'time/end_time.txt')
    if os.path.exists(end_time_file):
        f_end = open(end_time_file, "r")
        end_time_strip = f_end.read()
    return end_time_strip



def create_sample_directory(project_name, email, analysis_code, sample_list):
    datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                        project_name + '_' + email + '_' + analysis_code)
    for sample in sample_list:
        sample_dir = os.path.join(datadir, sample)
        if not os.path.exists(sample_dir):
            os.makedirs(sample_dir)


def create_time_directory(project_name, email, analysis_code):
    datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                        project_name + '_' + email + '_' + analysis_code)
    time_dir = os.path.join(datadir, "time")
    if not os.path.exists(time_dir):
        os.makedirs(time_dir)

########################
### Checking session ###
########################
def check_session(request):
    project_name = None
    analysis_code = None
    email = None
    assembly_type_input = None
    if 'project_name' in request.session:
        project_name = request.session['project_name']
        print("project_name: ", project_name)
        request.session["project_name"] = project_name
    if 'analysis_code' in request.session:
        analysis_code = request.session['analysis_code']
        print("analysis_code: ", analysis_code)
        request.session["analysis_code"] = analysis_code
    if 'email' in request.session:
        email = request.session['email']
        print("email: ", email)
        request.session["email"] = email
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    return (project_name, analysis_code, email, assembly_type_input)


#########################
### Checking samples! ###
#########################
def check_samples_txt_file(base_dir):
    sample_file_validity = True
    sample_file_two_or_one = 0
    samples_txt_file_name = None
    samples_list_key = {}
    sample_list = []
    samples_txt_file = os.path.join(base_dir, 'samples.csv')
    samples_txt_file_ans = os.path.exists(samples_txt_file)
    if samples_txt_file_ans:
        samples_txt_file_name = samples_txt_file
        read_ans = pandas.read_csv(samples_txt_file)
        header_names = list(read_ans)
        # First check column names
        if 'ids' not in header_names or 'Groups' not in header_names:
            sample_file_validity = False
        # Second check ids in the file are distinct
        if not len(read_ans['ids'].unique()) == len(read_ans['ids']):
            sample_file_validity = False
        # Third check types of Groups are only two
        # if not len(read_ans['Groups'].unique()) == 2 :
        #     sample_file_validity = False
        # Now check the sample group number
        if len(read_ans['Groups'].unique()) == 1:
            sample_file_two_or_one = 1
        elif len(read_ans['Groups'].unique()) == 2:
            sample_file_two_or_one = 2
        else:
            sample_file_validity = False
            sample_file_two_or_one = 0

        # Whether both numbers should be the same ??
        samples_groups = read_ans['Groups'].unique()
        samples_names = read_ans['ids'].unique()
        for i in samples_groups:
            group_samples = read_ans[read_ans['Groups'] == i]['ids'].tolist()
            samples_list_key[i] = group_samples
        for j in samples_names:
            sample_list.append(j)
        return (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one)

    else:
        return (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one)


#########################
### Checking fastq.gz ###
#########################
def check_uploaded_fastq_file(project_name, email, analysis_code):
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    url_base_dir = os.path.join('/media', 'tmp', project_name + '_' + email + '_' + analysis_code)
    samples_txt_file = os.path.join(base_dir, 'samples.csv')
    samples_txt_file_ans = os.path.exists(samples_txt_file)
    check_uploaded_fastq_file_ans = {}
    if samples_txt_file_ans:
        samples_file = pandas.read_csv(samples_txt_file)
        samples_names = samples_file['ids'].unique().tolist()
        for sample in samples_names:
            one_sample_pe_file_ans = {}
            r1 = os.path.join(base_dir, "Uploaded_files", sample, sample+".R1.fastq.gz")
            r2 = os.path.join(base_dir, "Uploaded_files", sample, sample+".R2.fastq.gz")
            one_sample_pe_file_ans['R1_checker'] = os.path.exists(r1)
            if os.path.exists(r1):
                one_sample_pe_file_ans['R1_url'] = os.path.join(url_base_dir, "Uploaded_files", sample, sample+".R1.fastq.gz")
            else:
                one_sample_pe_file_ans['R1_url'] = "#"
            one_sample_pe_file_ans['R2_checker'] = os.path.exists(r2)
            if os.path.exists(r2):
                one_sample_pe_file_ans['R2_url'] = os.path.join(url_base_dir, "Uploaded_files", sample, sample+".R2.fastq.gz")
            else:
                one_sample_pe_file_ans['R2_url'] = "#"
            check_uploaded_fastq_file_ans[sample] = one_sample_pe_file_ans
    return check_uploaded_fastq_file_ans


def check_uploaded_fastq_file_whole_answer(check_uploaded_fastq_file_ans):
    all_final_fastq_ans_list = []
    for sample, ans in check_uploaded_fastq_file_ans.items():
        r1_ans = ans["R1_checker"]
        all_final_fastq_ans_list.append(r1_ans)
        r2_ans = ans["R2_checker"]
        all_final_fastq_ans_list.append(r2_ans)
    ## Check every condition is true
    all_final_fastq_ans = all(all_final_fastq_ans_list)
    return all_final_fastq_ans

# Check the step with whole samples


######################
### Checking files ###
######################
def check_submission_time_file(base_dir, sample_name):
    submission_time_file = os.path.join(base_dir, 'time/submision_time.txt')
    submission_time_file_ans = os.path.exists(submission_time_file)
    if submission_time_file_ans:
        return True
    else:
        return False

def check_start_time_file(base_dir, sample_name):
    start_time_file = os.path.join(base_dir, 'time/start_time.txt')
    start_time_file_ans = os.path.exists(start_time_file)
    if start_time_file_ans:
        return True
    else:
        return False

def check_end_time_file(base_dir, sample_name):
    end_time_file = os.path.join(settings.MEDIA_ROOT, 'tmp', base_dir, 'time/end_time.txt')
    end_time_file_ans = os.path.exists(end_time_file)
    if end_time_file_ans:
        return True
    else:
        return False



def Step_1_check_first_qc(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, 'Step_1', 'QC', 'pre')
    url_root_dir = os.path.join(url_base_dir, 'Step_1', 'QC', 'pre')
    # print("**** Inside check_first_qc function:")
    # print("R1 html: ", os.path.join(root_dir, sample_name+".R1_fastqc.html"))
    # print("R2 html: ", os.path.join(root_dir, sample_name+".R2_fastqc.html"))
    # print("R1 zip: ", os.path.join(root_dir, sample_name+".R1_fastqc.zip"))
    # print("R2 zip: ", os.path.join(root_dir, sample_name+".R2_fastqc.zip"))
    # print("multiqc html: ", os.path.join(root_dir, sample_name+"_multiqc.html"))
    # print("multiqc dir: ", os.path.join(
    #     root_dir, sample_name+"_multiqc_data"))
    r1_html = os.path.exists(os.path.join(root_dir, sample_name+".R1_fastqc.html"))
    r2_html = os.path.exists(os.path.join(root_dir, sample_name+".R2_fastqc.html"))
    r1_zip = os.path.exists(os.path.join(root_dir, sample_name+".R1_fastqc.zip"))
    r2_zip = os.path.exists(os.path.join(root_dir, sample_name+".R2_fastqc.zip"))
    multiqc_html = os.path.exists(os.path.join(root_dir, sample_name+"_multiqc.html"))
    multiqc_dir = os.path.exists(os.path.join(root_dir, sample_name+"_multiqc_data"))
    # print("r1_html: ", r1_html)
    # print("r2_html: ", r2_html)
    # print("r1_zip: ", r1_zip)
    # print("r2_zip: ", r2_zip)
    # print("multiqc_html: ", multiqc_html)
    # print("multiqc_dir: ", multiqc_dir)
    Step_1_check_first_qc_urls = {}
    if r1_html and r2_html and r1_zip and r2_zip and multiqc_html and multiqc_dir:
        url_r1_html = os.path.join(url_root_dir, sample_name+".R1_fastqc.html")
        Step_1_check_first_qc_urls["url_r1_html"] = url_r1_html
        url_r2_html = os.path.join(url_root_dir, sample_name+".R2_fastqc.html")
        Step_1_check_first_qc_urls["url_r2_html"] = url_r2_html
        url_r1_zip = os.path.join(url_root_dir, sample_name+".R1_fastqc.zip")
        Step_1_check_first_qc_urls["url_r1_zip"] = url_r1_zip
        url_r2_zip = os.path.join(url_root_dir, sample_name+".R2_fastqc.zip")
        Step_1_check_first_qc_urls["url_r2_zip"] = url_r2_zip
        url_multiqc_html = os.path.join(url_root_dir, sample_name+"_multiqc.html")
        Step_1_check_first_qc_urls["url_multiqc_html"] = url_multiqc_html
        url_multiqc_dir = os.path.join(url_root_dir, sample_name+"_multiqc_data")
        Step_1_check_first_qc_urls["url_multiqc_dir"] = url_multiqc_dir
        return (True, Step_1_check_first_qc_urls)
    else:
        return (False, Step_1_check_first_qc_urls)


def Step_1_check_trimming_qc(url_base_dir, sample_datadir, sample_name):
    root_dir_trimmed_paired = os.path.join(sample_datadir, 'Step_1', "trimmed_paired")
    url_root_dir_trimmed_paired = os.path.join(url_base_dir, 'Step_1', "trimmed_paired")
    root_dir_trimmed_unpaired = os.path.join(sample_datadir, 'Step_1', "trimmed_unpaired")
    url_root_dir_trimmed_unpaired = os.path.join(url_base_dir, 'Step_1', "trimmed_unpaired")
    # print("**** Inside trimmomatic_pe_target function:")
    # print("r1_paired: ", os.path.join(
    #     root_dir_trimmed_paired, sample_name+"_r1_paired.fastq.gz"))
    # print("r2_paired: ", os.path.join(
    #     root_dir_trimmed_paired, sample_name+"_r2_paired.fastq.gz"))
    # print("r1_unpaired: ", os.path.join(
    #     root_dir_trimmed_unpaired, sample_name+"_r1_unpaired.fastq.gz"))
    # print("r2_unpaired: ", os.path.join(
    #     root_dir_trimmed_unpaired, sample_name+"_r2_unpaired.fastq.gz"))
    r1_paired = os.path.exists(os.path.join(
        root_dir_trimmed_paired, sample_name+"_r1_paired.fastq.gz"))
    r2_paired = os.path.exists(os.path.join(
        root_dir_trimmed_paired, sample_name+"_r2_paired.fastq.gz"))
    r1_unpaired = os.path.exists(os.path.join(
        root_dir_trimmed_unpaired, sample_name+"_r1_unpaired.fastq.gz"))
    r2_unpaired = os.path.exists(os.path.join(
        root_dir_trimmed_unpaired, sample_name+"_r2_unpaired.fastq.gz"))
    # print("r1_paired: ", r1_paired)
    # print("r2_paired: ", r2_paired)
    # print("r1_unpaired: ", r1_unpaired)
    # print("r2_unpaired: ", r2_unpaired)
    Step_1_check_trimming_qc_urls = {}
    if r1_paired and r2_paired and r1_unpaired and r2_unpaired:
        url_r1_paired = os.path.join(url_root_dir_trimmed_paired, sample_name+"_r1_paired.fastq.gz")
        Step_1_check_trimming_qc_urls["url_r1_paired"] = url_r1_paired
        url_r2_paired = os.path.join(url_root_dir_trimmed_paired, sample_name+"_r2_paired.fastq.gz")
        Step_1_check_trimming_qc_urls["url_r2_paired"] = url_r2_paired
        url_r1_unpaired = os.path.join(url_root_dir_trimmed_unpaired, sample_name+"_r1_unpaired.fastq.gz")
        Step_1_check_trimming_qc_urls["url_r1_unpaired"] = url_r1_unpaired
        url_r2_unpaired = os.path.join(url_root_dir_trimmed_unpaired, sample_name+"_r2_unpaired.fastq.gz")
        Step_1_check_trimming_qc_urls["url_r2_unpaired"] = url_r2_unpaired
        return (True, Step_1_check_trimming_qc_urls)
    else:
        return (False, Step_1_check_trimming_qc_urls)


def Step_1_check_second_qc(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, 'Step_1', 'QC', 'post')
    url_root_dir = os.path.join(url_base_dir, 'Step_1', 'QC', 'post')
    r1_paired_html = os.path.exists(os.path.join(root_dir, sample_name+"_r1_paired_fastqc.html"))
    # r1_unpaired_html = os.path.exists(os.path.join(
    #     root_dir, sample_name+"_r1_unpaired_fastqc.html"))
    r2_paired_html = os.path.exists(os.path.join(root_dir, sample_name+"_r2_paired_fastqc.html"))
    # r2_unpaired_html = os.path.exists(os.path.join(
    #     root_dir, sample_name+"_r2_unpaired_fastqc.html"))
    r1_paired_zip = os.path.exists(os.path.join(root_dir, sample_name+"_r1_paired_fastqc.zip"))
    # r1_unpaired_zip = os.path.exists(os.path.join(
    #     root_dir, sample_name+"_r1_unpaired_fastqc.zip"))
    r2_paired_zip = os.path.exists(os.path.join(root_dir, sample_name+"_r2_paired_fastqc.zip"))
    # r2_unpaired_zip = os.path.exists(os.path.join(
    #     root_dir, sample_name+"_r2_unpaired_fastqc.zip"))
    multiqc_html = os.path.exists(os.path.join(root_dir, sample_name+"_multiqc.html"))
    multiqc_dir = os.path.exists(os.path.join(root_dir, sample_name+"_multiqc_data"))
    # print("r1_paired_html: ", r1_paired_html)
    # # print("r1_unpaired_html: ", r1_unpaired_html)
    # print("r2_paired_html: ", r2_paired_html)
    # # print("r2_unpaired_html: ", r2_unpaired_html)
    # print("r1_paired_zip: ", r1_paired_zip)
    # # print("r1_unpaired_zip: ", r1_unpaired_zip)
    # print("r2_paired_zip: ", r2_paired_zip)
    # # print("r2_unpaired_zip: ", r2_unpaired_zip)
    # print("multiqc_html: ", multiqc_html)
    # print("multiqc_dir: ", multiqc_dir)
    Step_1_check_second_qc_urls = {}
    if r1_paired_html and r2_paired_html and r1_paired_zip and r2_paired_zip and multiqc_html and multiqc_dir:
        r1_paired_html = os.path.join(url_root_dir, sample_name+"_r1_paired_fastqc.html")
        Step_1_check_second_qc_urls["r1_paired_html"] = r1_paired_html
        r2_paired_html = os.path.join(url_root_dir, sample_name+"_r2_paired_fastqc.html")
        Step_1_check_second_qc_urls["r2_paired_html"] = r2_paired_html
        r1_paired_zip = os.path.join(url_root_dir, sample_name+"_r1_paired_fastqc.zip")
        Step_1_check_second_qc_urls["r1_paired_zip"] = r1_paired_zip
        r2_paired_zip = os.path.join(url_root_dir, sample_name+"_r2_paired_fastqc.zip")
        Step_1_check_second_qc_urls["r2_paired_zip"] = r2_paired_zip
        multiqc_html = os.path.join(url_root_dir, sample_name+"_multiqc.html")
        Step_1_check_second_qc_urls["multiqc_html"] = multiqc_html
        multiqc_dir = os.path.join(url_root_dir, sample_name+"_multiqc_data")
        Step_1_check_second_qc_urls["multiqc_dir"] = multiqc_dir
        return (True, Step_1_check_second_qc_urls)
    else:
        return (False, Step_1_check_second_qc_urls)

################################
### reference-based specific ###
################################
def Step_2_check_reference_based_bwa_sam(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_2", "bwa")
    url_root_dir = os.path.join(url_base_dir, "Step_2", "bwa")
    # print("bwa sam file: ", os.path.join(
    #     root_dir, sample_name+".sam"))
    reference_based_bwa_sam = os.path.exists(os.path.join(
        root_dir, sample_name+".sam"))
    # print("reference_based_bwa_sam: ", reference_based_bwa_sam)
    Step_2_check_reference_based_bwa_sam_urls = {}
    if reference_based_bwa_sam:
        url_reference_based_bwa_sam = os.path.join(url_root_dir, sample_name+".sam")
        Step_2_check_reference_based_bwa_sam_urls["url_reference_based_bwa_sam"] = url_reference_based_bwa_sam
        return (True, Step_2_check_reference_based_bwa_sam_urls)
    else:
        return (False, Step_2_check_reference_based_bwa_sam_urls)


def Step_2_check_reference_based_bwa_report_txt(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_2", "bwa")
    url_root_dir = os.path.join(url_base_dir, "Step_2", "bwa")
    # print("bwa report file: ", os.path.join(
    #     root_dir, sample_name+"_alignment_report.txt"))
    reference_based_bwa_report_txt = os.path.exists(os.path.join(
        root_dir, sample_name+"_alignment_report.txt"))
    # print("reference_based_bwa_report_txt: ", reference_based_bwa_report_txt)
    Step_2_check_reference_based_bwa_report_txt_urls = {}
    if reference_based_bwa_report_txt:
        url_reference_based_bwa_report_txt = os.path.join(url_root_dir, sample_name+"_alignment_report.txt")
        Step_2_check_reference_based_bwa_report_txt_urls["url_reference_based_bwa_report_txt"] = url_reference_based_bwa_report_txt
        return (True, Step_2_check_reference_based_bwa_report_txt_urls)
    else:
        return (False, Step_2_check_reference_based_bwa_report_txt_urls)





########################
### De novo assembly ###
########################
def Step_2_check_denovo_a5_miseq(url_base_dir, sample_datadir, sample_name):
    ## Check files before moving
    root_dir = os.path.join(sample_datadir, "Step_2", "a5_miseq")
    url_root_dir = os.path.join(url_base_dir, "Step_2", "a5_miseq")

    a5_dir = os.path.exists(os.path.join(root_dir, sample_name+"_a5"))
    a5_dir_s1 = os.path.exists(os.path.join(root_dir, sample_name+"_a5.s1"))
    a5_dir_s2 = os.path.exists(os.path.join(root_dir, sample_name+"_a5.s2"))
    a5_agp = os.path.exists(os.path.join(root_dir, sample_name+"_a5.agp"))
    a5_assembly_stats_csv = os.path.exists(os.path.join(root_dir, sample_name+"_a5.assembly_stats.csv"))
    a5_contigs_fasta = os.path.exists(os.path.join(root_dir, sample_name+"_a5.contigs.fasta"))
    a5_contigs_fastq = os.path.exists(os.path.join(root_dir, sample_name+"_a5.contigs.fastq"))
    a5_contigs_qvl = os.path.exists(os.path.join(root_dir, sample_name+"_a5.contigs.qvl"))
    a5_final_scaffolds_fasta_contigs_fsa = os.path.exists(os.path.join(root_dir, sample_name+"_a5.final.scaffolds.fasta.contigs.fsa"))
    a5_raw1_pe_sort_bam = os.path.exists(os.path.join(root_dir, sample_name+"_a5.raw1.pe.sort.bam"))
    a5_tmplibs = os.path.exists(os.path.join(root_dir, sample_name+"_a5.tmplibs"))
    Step_2_check_denovo_a5_miseq_urls = {}
    if a5_dir and a5_dir_s1 and a5_dir_s2 and a5_agp and a5_assembly_stats_csv and a5_contigs_fasta and a5_contigs_fastq and a5_contigs_qvl and a5_final_scaffolds_fasta_contigs_fsa and a5_raw1_pe_sort_bam and a5_tmplibs:
        url_a5_dir = os.path.join(url_root_dir, sample_name+"_a5")
        Step_2_check_denovo_a5_miseq_urls["url_a5_dir"] = url_a5_dir
        url_a5_dir_s1 = os.path.join(url_root_dir, sample_name+"_a5.s1")
        Step_2_check_denovo_a5_miseq_urls["url_a5_dir_s1"] = url_a5_dir_s1
        url_a5_dir_s2 = os.path.join(url_root_dir, sample_name+"_a5.s2")
        Step_2_check_denovo_a5_miseq_urls["url_a5_dir_s2"] = url_a5_dir_s2
        url_a5_agp = os.path.join(url_root_dir, sample_name+"_a5.agp")
        Step_2_check_denovo_a5_miseq_urls["url_a5_agp"] = url_a5_agp
        url_a5_assembly_stats_csv = os.path.join(url_root_dir, sample_name+"_a5.assembly_stats.csv")
        Step_2_check_denovo_a5_miseq_urls["url_a5_assembly_stats_csv"] = url_a5_assembly_stats_csv
        url_a5_contigs_fasta = os.path.join(url_root_dir, sample_name+"_a5.contigs.fasta")
        Step_2_check_denovo_a5_miseq_urls["url_a5_contigs_fasta"] = url_a5_contigs_fasta
        url_a5_contigs_fastq = os.path.join(url_root_dir, sample_name+"_a5.contigs.fastq")
        Step_2_check_denovo_a5_miseq_urls["url_a5_contigs_fastq"] = url_a5_contigs_fastq
        url_a5_contigs_qvl = os.path.join(url_root_dir, sample_name+"_a5.contigs.qvl")
        Step_2_check_denovo_a5_miseq_urls["url_a5_contigs_qvl"] = url_a5_contigs_qvl
        url_a5_final_scaffolds_fasta_contigs_fsa = os.path.join(url_root_dir, sample_name+"_a5.final.scaffolds.fasta.contigs.fsa")
        Step_2_check_denovo_a5_miseq_urls["url_a5_final_scaffolds_fasta_contigs_fsa"] = url_a5_final_scaffolds_fasta_contigs_fsa
        url_a5_raw1_pe_sort_bam = os.path.join(url_root_dir, sample_name+"_a5.raw1.pe.sort.bam")
        Step_2_check_denovo_a5_miseq_urls["url_a5_raw1_pe_sort_bam"] = url_a5_raw1_pe_sort_bam
        url_a5_tmplibs = os.path.join(url_root_dir, sample_name+"_a5.tmplibs")
        Step_2_check_denovo_a5_miseq_urls["url_a5_tmplibs"] = url_a5_tmplibs
        return (True, Step_2_check_denovo_a5_miseq_urls)
    else:
        return (False, Step_2_check_denovo_a5_miseq_urls)


def Step_3_check_quast_assessment(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_3", "quast")
    url_root_dir = os.path.join(url_base_dir, "Step_3", "quast")
    contig_size_viewer_html = os.path.exists(os.path.join("{sample}", "Step_3", "quast", "icarus_viewers", "contig_size_viewer.html")),
    icarus_html = os.path.exists(os.path.join(root_dir, "icarus.html"))
    report_html = os.path.exists(os.path.join(root_dir, "report.html"))
    report_tsv = os.path.exists(os.path.join(root_dir, "report.tsv"))

    report_tex = os.path.exists(os.path.join(root_dir, "report.tex"))
    report_txt = os.path.exists(os.path.join(root_dir, "report.txt"))
    transposed_report_tex = os.path.exists(os.path.join(root_dir, "transposed_report.tex"))
    transposed_report_tsv = os.path.exists(os.path.join(root_dir, "transposed_report.tsv"))
    transposed_report_txt = os.path.exists(os.path.join(root_dir, "transposed_report.txt"))

    report_pdf = os.path.exists(os.path.join(root_dir, "report.pdf"))
    Step_3_check_quast_assessment_urls = {}
    if contig_size_viewer_html and icarus_html and report_html and report_tsv and report_pdf :
        url_contig_size_viewer_html = os.path.join(url_root_dir, "icarus_viewers", "contig_size_viewer.html")
        Step_3_check_quast_assessment_urls["url_contig_size_viewer_html"] = url_contig_size_viewer_html
        url_icarus_html = os.path.join(url_root_dir, "icarus.html")
        Step_3_check_quast_assessment_urls["url_icarus_html"] = url_icarus_html
        url_report_html = os.path.join(url_root_dir, "report.html")
        Step_3_check_quast_assessment_urls["url_report_html"] = url_report_html
        url_report_tsv = os.path.join(url_root_dir, "report.tsv")
        Step_3_check_quast_assessment_urls["url_report_tsv"] = url_report_tsv
        url_report_tex = os.path.join(url_root_dir, "report.tex")
        Step_3_check_quast_assessment_urls["url_report_tex"] = url_report_tex
        url_report_txt = os.path.join(url_root_dir, "report.txt")
        Step_3_check_quast_assessment_urls["url_report_txt"] = url_report_txt
        url_transposed_report_tex = os.path.join(url_root_dir, "transposed_report.tex")
        Step_3_check_quast_assessment_urls["url_transposed_report_tex"] = url_transposed_report_tex
        url_transposed_report_tsv = os.path.join(url_root_dir, "transposed_report.tsv")
        Step_3_check_quast_assessment_urls["url_transposed_report_tsv"] = url_transposed_report_tsv
        url_transposed_report_txt = os.path.join(url_root_dir, "transposed_report.txt")
        Step_3_check_quast_assessment_urls["url_transposed_report_txt"] = url_transposed_report_txt
        url_report_pdf = os.path.join(url_root_dir, "report.pdf")
        Step_3_check_quast_assessment_urls["url_report_pdf"] = url_report_pdf
        return (True, Step_3_check_quast_assessment_urls)
    else:
        return (False, Step_3_check_quast_assessment_urls)

def Step_3_check_bowtie2_assessment(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_3", "bowtie2")
    url_root_dir = os.path.join(url_base_dir, "Step_3", "bowtie2")

    bowtie2_index_folder = os.path.exists(os.path.join(root_dir, "bowtie_index"))
    bowtie2_index_1 = os.path.exists(os.path.join(root_dir, "bowtie_index", sample_name+".1.bt2"))
    bowtie2_output_prefix = os.path.exists(os.path.join(root_dir, sample_name+".bam"))

    Step_3_check_bowtie2_assessment_urls = {}
    if bowtie2_index_folder and bowtie2_index_1 and bowtie2_output_prefix:
        url_bowtie2_index_folder = os.path.join(url_root_dir, "bowtie_index")
        Step_3_check_bowtie2_assessment_urls["url_bowtie2_index_folder"] = url_bowtie2_index_folder
        url_bowtie2_index_1 = os.path.join(url_root_dir, "bowtie_index", sample_name+".1.bt2")
        Step_3_check_bowtie2_assessment_urls["url_bowtie2_index_1"] = url_bowtie2_index_1
        url_bowtie2_output_prefix = os.path.join(url_root_dir, sample_name+".bam")
        Step_3_check_bowtie2_assessment_urls["url_bowtie2_output_prefix"] = url_bowtie2_output_prefix
        return (True, Step_3_check_bowtie2_assessment_urls)
    else:
        return (False, Step_3_check_bowtie2_assessment_urls)

def Step_4_check_denovo_samtools_fixmate_bam(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_4", "samtools")
    url_root_dir = os.path.join(url_base_dir, "Step_4", "samtools")
    # print("fixmate bam file: ", os.path.join(
    #     root_dir, sample_name+"_fixmate.bam"))
    denovo_samtools_fixmate_bam = os.path.exists(os.path.join(root_dir, sample_name+"_fixmate.bam"))
    # print("reference_based_samtools_fixmate_bam: ", reference_based_samtools_fixmate_bam)
    Step_4_check_denovo_samtools_fixmate_bam_urls = {}
    if denovo_samtools_fixmate_bam:
        url_denovo_samtools_fixmate_bam = os.path.join(url_root_dir, sample_name+"_fixmate.bam")
        Step_4_check_denovo_samtools_fixmate_bam_urls["url_denovo_samtools_fixmate_bam"] = url_denovo_samtools_fixmate_bam
        return (True, Step_4_check_denovo_samtools_fixmate_bam_urls)
    else:
        return (False, Step_4_check_denovo_samtools_fixmate_bam_urls)

def Step_4_check_denovo_samtools_sorted_bam(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_4", "samtools")
    url_root_dir = os.path.join(url_base_dir, "Step_4", "samtools")
    # print("sorted bam file: ", os.path.join(
    #     root_dir, sample_name+"_sorted.bam"))
    denovo_samtools_sorted_bam = os.path.exists(os.path.join(
        root_dir, sample_name+"_sorted.bam"))
    # print("reference_based_samtools_sorted_bam: ", reference_based_samtools_sorted_bam)
    Step_4_check_denovo_samtools_sorted_bam_urls = {}
    if denovo_samtools_sorted_bam:
        url_denovo_samtools_sorted_bam = os.path.join(url_root_dir, sample_name+"_sorted.bam")
        Step_4_check_denovo_samtools_sorted_bam_urls["url_denovo_samtools_sorted_bam"] = url_denovo_samtools_sorted_bam
        return (True, Step_4_check_denovo_samtools_sorted_bam_urls)
    else:
        return (False, Step_4_check_denovo_samtools_sorted_bam_urls)

def Step_5_check_denovo_bcftools_vcf(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_5", "bcftools")
    url_root_dir = os.path.join(url_base_dir, "Step_5", "bcftools")
    # print("bcftools vcf_gz file: ", os.path.join(
    #     root_dir, sample_name+".vcf"))
    denovo_bcftools_vcf = os.path.exists(os.path.join(root_dir, sample_name+".vcf"))
    # print("reference_based_bcftools_vcf: ", reference_based_bcftools_vcf)
    Step_5_check_denovo_bcftools_vcf_urls = {}
    if denovo_bcftools_vcf:
        url_denovo_bcftools_vcf = os.path.join(url_root_dir, sample_name+".vcf")
        Step_5_check_denovo_bcftools_vcf_urls["url_denovo_bcftools_vcf"] = url_denovo_bcftools_vcf
        return (True, Step_5_check_denovo_bcftools_vcf_urls)
    else:
        return (False, Step_5_check_denovo_bcftools_vcf_urls)

def Step_5_check_denovo_bcftools_vcf_revise(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_5", "bcftools")
    url_root_dir = os.path.join(url_base_dir, "Step_5", "bcftools")
    # print("bcftools vcf_gz file: ", os.path.join(
    #     root_dir, sample_name+"_revise.vcf"))
    denovo_bcftools_vcf_revise = os.path.exists(os.path.join(root_dir, sample_name+"_revise.vcf"))
    # print("reference_based_bcftools_vcf_revise: ", reference_based_bcftools_vcf_revise)
    Step_5_check_reference_based_bcftools_vcf_revise_urls = {}
    if denovo_bcftools_vcf_revise:
        url_denovo_bcftools_vcf_revise = os.path.join(url_root_dir, sample_name+"_revise.vcf")
        Step_5_check_reference_based_bcftools_vcf_revise_urls["url_denovo_bcftools_vcf_revise"] = url_denovo_bcftools_vcf_revise
        return (True, Step_5_check_reference_based_bcftools_vcf_revise_urls)
    else:
        return (False, Step_5_check_reference_based_bcftools_vcf_revise_urls)

def Step_6_check_denovo_snpeff_vcf_annotation(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_6", "snpeff")
    url_root_dir = os.path.join(url_base_dir, "Step_6", "snpeff")
    # print("snpeff annotation file: ", os.path.join(
    #     root_dir, sample_name+".ann.vcf"))
    # print("snpeff annotation file: ", os.path.join(
    #     root_dir, sample_name+"_snpEff_summary.genes.txt"))
    # print("snpeff annotation file: ", os.path.join(
    #     root_dir, sample_name+"_snpEff_summary.html"))
    denovo_snpeff_vcf_annotation = os.path.exists(os.path.join(root_dir, sample_name+".ann.vcf"))
    denovo_snpeff_vcf_annotation_txt = os.path.exists(os.path.join(root_dir, sample_name+"_snpEff_summary.genes.txt"))
    denovo_snpeff_vcf_annotation_html = os.path.exists(os.path.join(root_dir, sample_name+"_snpEff_summary.html"))
    # print("reference_based_snpeff_vcf_annotation: ", denovo_snpeff_vcf_annotation)
    # print("reference_based_snpeff_vcf_annotation_txt: ", denovo_snpeff_vcf_annotation_txt)
    # print("reference_based_snpeff_vcf_annotation_html: ", denovo_snpeff_vcf_annotation_html)
    Step_6_check_reference_based_snpeff_vcf_annotation_urls = {}
    if denovo_snpeff_vcf_annotation and denovo_snpeff_vcf_annotation_txt and denovo_snpeff_vcf_annotation_html:
        url_denovo_snpeff_vcf_annotation = os.path.join(url_root_dir, sample_name+".ann.vcf")
        url_denovo_snpeff_vcf_annotation_txt = os.path.join(url_root_dir, sample_name+"_snpEff_summary.genes.txt")
        url_denovo_snpeff_vcf_annotation_html = os.path.join(url_root_dir, sample_name+"_snpEff_summary.html")
        Step_6_check_reference_based_snpeff_vcf_annotation_urls["url_denovo_snpeff_vcf_annotation"] = url_denovo_snpeff_vcf_annotation
        Step_6_check_reference_based_snpeff_vcf_annotation_urls["url_denovo_snpeff_vcf_annotation_txt"] = url_denovo_snpeff_vcf_annotation_txt
        Step_6_check_reference_based_snpeff_vcf_annotation_urls["url_denovo_snpeff_vcf_annotation_html"] = url_denovo_snpeff_vcf_annotation_html
        return (True, Step_6_check_reference_based_snpeff_vcf_annotation_urls)
    else:
        return (False, Step_6_check_reference_based_snpeff_vcf_annotation_urls)

















def Step_3_check_reference_based_samtools_fixmate_bam(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_3", "samtools")
    url_root_dir = os.path.join(url_base_dir, "Step_3", "samtools")
    # print("fixmate bam file: ", os.path.join(
    #     root_dir, sample_name+"_fixmate.bam"))
    reference_based_samtools_fixmate_bam = os.path.exists(os.path.join(
        root_dir, sample_name+"_fixmate.bam"))
    # print("reference_based_samtools_fixmate_bam: ", reference_based_samtools_fixmate_bam)
    Step_3_check_reference_based_samtools_fixmate_bam_urls = {}
    if reference_based_samtools_fixmate_bam:
        url_reference_based_samtools_fixmate_bam = os.path.join(url_root_dir, sample_name+"_fixmate.bam")
        Step_3_check_reference_based_samtools_fixmate_bam_urls["url_reference_based_samtools_fixmate_bam"] = url_reference_based_samtools_fixmate_bam
        return (True, Step_3_check_reference_based_samtools_fixmate_bam_urls)
    else:
        return (False, Step_3_check_reference_based_samtools_fixmate_bam_urls)

def Step_3_check_reference_based_samtools_sorted_bam(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_3", "samtools")
    url_root_dir = os.path.join(url_base_dir, "Step_3", "samtools")
    # print("sorted bam file: ", os.path.join(
    #     root_dir, sample_name+"_sorted.bam"))
    reference_based_samtools_sorted_bam = os.path.exists(os.path.join(
        root_dir, sample_name+"_sorted.bam"))
    # print("reference_based_samtools_sorted_bam: ", reference_based_samtools_sorted_bam)
    Step_3_check_reference_based_samtools_sorted_bam_urls = {}
    if reference_based_samtools_sorted_bam:
        url_reference_based_samtools_sorted_bam = os.path.join(url_root_dir, sample_name+"_sorted.bam")
        Step_3_check_reference_based_samtools_sorted_bam_urls["url_reference_based_samtools_sorted_bam"] = url_reference_based_samtools_sorted_bam
        return (True, Step_3_check_reference_based_samtools_sorted_bam_urls)
    else:
        return (False, Step_3_check_reference_based_samtools_sorted_bam_urls)


def Step_4_check_reference_based_bcftools_vcf(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_4", "bcftools")
    url_root_dir = os.path.join(url_base_dir, "Step_4", "bcftools")
    # print("bcftools vcf_gz file: ", os.path.join(
    #     root_dir, sample_name+".vcf"))
    reference_based_bcftools_vcf = os.path.exists(os.path.join(
        root_dir, sample_name+".vcf"))
    # print("reference_based_bcftools_vcf: ", reference_based_bcftools_vcf)
    Step_4_check_reference_based_bcftools_vcf_urls = {}
    if reference_based_bcftools_vcf:
        url_reference_based_bcftools_vcf = os.path.join(url_root_dir, sample_name+".vcf")
        Step_4_check_reference_based_bcftools_vcf_urls["url_reference_based_bcftools_vcf"] = url_reference_based_bcftools_vcf
        return (True, Step_4_check_reference_based_bcftools_vcf_urls)
    else:
        return (False, Step_4_check_reference_based_bcftools_vcf_urls)

def Step_4_check_reference_based_bcftools_vcf_revise(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_4", "bcftools")
    url_root_dir = os.path.join(url_base_dir, "Step_4", "bcftools")
    # print("bcftools vcf_gz file: ", os.path.join(
    #     root_dir, sample_name+"_revise.vcf"))
    reference_based_bcftools_vcf_revise = os.path.exists(os.path.join(
        root_dir, sample_name+"_revise.vcf"))
    # print("reference_based_bcftools_vcf_revise: ", reference_based_bcftools_vcf_revise)
    Step_4_check_reference_based_bcftools_vcf_revise_urls = {}
    if reference_based_bcftools_vcf_revise:
        reference_based_bcftools_vcf_revise = os.path.join(url_root_dir, sample_name+"_revise.vcf")
        Step_4_check_reference_based_bcftools_vcf_revise_urls["reference_based_bcftools_vcf_revise"] = reference_based_bcftools_vcf_revise
        return (True, Step_4_check_reference_based_bcftools_vcf_revise_urls)
    else:
        return (False, Step_4_check_reference_based_bcftools_vcf_revise_urls)

def Step_5_check_reference_based_snpeff_vcf_annotation(url_base_dir, sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Step_5", "snpeff")
    url_root_dir = os.path.join(url_base_dir, "Step_5", "snpeff")
    # print("snpeff annotation file: ", os.path.join(
    #     root_dir, sample_name+".ann.vcf"))
    # print("snpeff annotation file: ", os.path.join(
    #     root_dir, sample_name+"_snpEff_summary.genes.txt"))
    # print("snpeff annotation file: ", os.path.join(
    #     root_dir, sample_name+"_snpEff_summary.html"))
    reference_based_snpeff_vcf_annotation = os.path.exists(os.path.join(
        root_dir, sample_name+".ann.vcf"))
    reference_based_snpeff_vcf_annotation_txt = os.path.exists(os.path.join(
        root_dir, sample_name+"_snpEff_summary.genes.txt"))
    reference_based_snpeff_vcf_annotation_html = os.path.exists(os.path.join(
        root_dir, sample_name+"_snpEff_summary.html"))
    # print("reference_based_snpeff_vcf_annotation: ", reference_based_snpeff_vcf_annotation)
    # print("reference_based_snpeff_vcf_annotation_txt: ", reference_based_snpeff_vcf_annotation_txt)
    # print("reference_based_snpeff_vcf_annotation_html: ", reference_based_snpeff_vcf_annotation_html)
    Step_5_check_reference_based_snpeff_vcf_annotation_urls = {}
    if reference_based_snpeff_vcf_annotation and reference_based_snpeff_vcf_annotation_txt and reference_based_snpeff_vcf_annotation_html:
        reference_based_snpeff_vcf_annotation = os.path.join(url_root_dir, sample_name+".ann.vcf")
        reference_based_snpeff_vcf_annotation_txt = os.path.join(url_root_dir, sample_name+"_snpEff_summary.genes.txt")
        reference_based_snpeff_vcf_annotation_html = os.path.join(url_root_dir, sample_name+"_snpEff_summary.html")
        Step_5_check_reference_based_snpeff_vcf_annotation_urls["reference_based_snpeff_vcf_annotation"] = reference_based_snpeff_vcf_annotation
        Step_5_check_reference_based_snpeff_vcf_annotation_urls["reference_based_snpeff_vcf_annotation_txt"] = reference_based_snpeff_vcf_annotation_txt
        Step_5_check_reference_based_snpeff_vcf_annotation_urls["reference_based_snpeff_vcf_annotation_html"] = reference_based_snpeff_vcf_annotation_html
        return (True, Step_5_check_reference_based_snpeff_vcf_annotation_urls)
    else:
        return (False, Step_5_check_reference_based_snpeff_vcf_annotation_urls)


######################
### Virus assembly ###
######################
def check_bwa_subtraction_bwa_mem(url_base_dir, sample_datadir, sample_name):
    # sam_file = os.path.join("{sample}", "Step_2", "bwa_subtraction_bwa_mem", "{sample}.sam"),
    root_dir_bwa_mem = os.path.join(sample_datadir, 'Step_2', "bwa_subtraction_bwa_mem")
    url_root_bwa_mem = os.path.join(url_base_dir, 'Step_2', "bwa_subtraction_bwa_mem")

    bwa_mem_sam = os.path.exists(os.path.join(
        root_dir_bwa_mem, sample_name+".sam"))
    # print("bwa_mem_sam: ", bwa_mem_sam)
    Step_2_check_bwa_subtraction_bwa_mem = {}
    if bwa_mem_sam:
        url_bwa_mem_sam = os.path.join(url_root_bwa_mem, sample_name+".sam")
        Step_2_check_bwa_subtraction_bwa_mem["url_bwa_mem_sam"] = url_bwa_mem_sam
        return (True, Step_2_check_bwa_subtraction_bwa_mem)
    else:
        return (False, Step_2_check_bwa_subtraction_bwa_mem)

def check_bwa_subtraction_samtools_sam2bam(url_base_dir, sample_datadir, sample_name):
    # bam_file = os.path.join("{sample}", "Step_2", "bwa_subtraction_samtools_sam2bam", "{sample}.bam"),
    root_dir_samtools_sam2bam = os.path.join(sample_datadir, 'Step_2', "bwa_subtraction_samtools_sam2bam")
    url_root_samtools_sam2bam = os.path.join(url_base_dir, 'Step_2', "bwa_subtraction_samtools_sam2bam")

    samtools_sam2bam = os.path.exists(os.path.join(
        root_dir_samtools_sam2bam, sample_name+".bam"))
    # print("samtools_sam2bam: ", samtools_sam2bam)
    Step_2_check_bwa_subtraction_samtools_sam2bam = {}
    if samtools_sam2bam:
        url_samtools_sam2bam = os.path.join(url_root_samtools_sam2bam, sample_name+".bam")
        Step_2_check_bwa_subtraction_samtools_sam2bam["url_samtools_sam2bam"] = url_samtools_sam2bam
        return (True, Step_2_check_bwa_subtraction_samtools_sam2bam)
    else:
        return (False, Step_2_check_bwa_subtraction_samtools_sam2bam)

def check_bwa_subtraction_samtools_flagstat(url_base_dir, sample_datadir, sample_name):
    # txt_file = os.path.join("{sample}", "Step_2", "bwa_subtraction_samtools_flagstat", "{sample}.txt"),
    root_dir_samtools_flagstat = os.path.join(sample_datadir, 'Step_2', "bwa_subtraction_samtools_flagstat")
    url_root_samtools_flagstat = os.path.join(url_base_dir, 'Step_2', "bwa_subtraction_samtools_flagstat")

    samtools_flagstat_txt = os.path.exists(os.path.join(
        root_dir_samtools_flagstat, sample_name+".txt"))
    # print("samtools_flagstat_txt: ", samtools_flagstat_txt)
    Step_2_check_bwa_subtraction_samtools_flagstat = {}
    if samtools_flagstat_txt:
        url_samtools_flagstat_txt = os.path.join(url_root_samtools_flagstat, sample_name+".txt")
        Step_2_check_bwa_subtraction_samtools_flagstat["url_samtools_flagstat_txt"] = url_samtools_flagstat_txt
        return (True, Step_2_check_bwa_subtraction_samtools_flagstat)
    else:
        return (False, Step_2_check_bwa_subtraction_samtools_flagstat)

def check_bwa_subtraction_samtools_view_unmapped_bam(url_base_dir, sample_datadir, sample_name):
    # unmapped_bam_file = os.path.join("{sample}", "Step_2", "bwa_subtraction_samtools_view_unmapped_bam", "{sample}_unmapped.bam"),
    root_dir_samtools_view_unmapped_bam = os.path.join(sample_datadir, 'Step_2', "bwa_subtraction_samtools_view_unmapped_bam")
    url_root_samtools_view_unmapped_bam = os.path.join(url_base_dir, 'Step_2', "bwa_subtraction_samtools_view_unmapped_bam")

    samtools_view_unmapped_bam = os.path.exists(os.path.join(
        root_dir_samtools_view_unmapped_bam, sample_name+"_unmapped.bam"))
    # print("samtools_view_unmapped_bam: ", samtools_view_unmapped_bam)
    Step_2_check_bwa_subtraction_samtools_view_unmapped_bam = {}
    if samtools_view_unmapped_bam:
        url_samtools_view_unmapped_bam = os.path.join(url_root_samtools_view_unmapped_bam, sample_name+"_unmapped.bam")
        Step_2_check_bwa_subtraction_samtools_view_unmapped_bam["url_samtools_view_unmapped_bam"] = url_samtools_view_unmapped_bam
        return (True, Step_2_check_bwa_subtraction_samtools_view_unmapped_bam)
    else:
        return (False, Step_2_check_bwa_subtraction_samtools_view_unmapped_bam)

def check_bwa_subtraction_samtools_view_unmapped_sorted_bam(url_base_dir, sample_datadir, sample_name):
    # unmapped_bam_sorted_file = os.path.join("{sample}", "Step_2", "bwa_subtraction_samtools_view_unmapped_sorted_bam", "{sample}_sorted_unmapped.bam"),
    root_dir_samtools_view_unmapped_sorted_bam = os.path.join(sample_datadir, 'Step_2', "bwa_subtraction_samtools_view_unmapped_sorted_bam")
    url_root_samtools_view_unmapped_sorted_bam = os.path.join(url_base_dir, 'Step_2', "bwa_subtraction_samtools_view_unmapped_sorted_bam")

    samtools_view_unmapped_sorted_bam = os.path.exists(os.path.join(
        root_dir_samtools_view_unmapped_sorted_bam, sample_name+"_sorted_unmapped.bam"))
    # print("samtools_view_unmapped_sorted_bam: ", samtools_view_unmapped_sorted_bam)
    Step_2_check_bwa_subtraction_samtools_view_unmapped_sorted_bam = {}
    if samtools_view_unmapped_sorted_bam:
        url_samtools_view_unmapped_sorted_bam = os.path.join(url_root_samtools_view_unmapped_sorted_bam, sample_name+"_sorted_unmapped.bam")
        Step_2_check_bwa_subtraction_samtools_view_unmapped_sorted_bam["url_samtools_view_unmapped_sorted_bam"] = url_samtools_view_unmapped_sorted_bam
        return (True, Step_2_check_bwa_subtraction_samtools_view_unmapped_sorted_bam)
    else:
        return (False, Step_2_check_bwa_subtraction_samtools_view_unmapped_sorted_bam)

def check_bwa_subtraction_bedtools_bam2fastq(url_base_dir, sample_datadir, sample_name):
    # unmapped_fastq_r1 = os.path.join("{sample}", "Step_2", "bwa_subtraction_bedtools_bam2fastq", "{sample}_unmapped_r1.fastq.gz"),
    # unmapped_fastq_r2 = os.path.join("{sample}", "Step_2", "bwa_subtraction_bedtools_bam2fastq", "{sample}_unmapped_r2.fastq.gz"),
    root_dir_bam2fastq = os.path.join(sample_datadir, 'Step_2', "bwa_subtraction_bedtools_bam2fastq")
    url_root_bam2fastq = os.path.join(url_base_dir, 'Step_2', "bwa_subtraction_bedtools_bam2fastq")
    r1_bam2fastq = os.path.exists(os.path.join(
        root_dir_bam2fastq, sample_name+"_unmapped_r1.fastq.gz"))
    r2_bam2fastq = os.path.exists(os.path.join(
        url_root_bam2fastq, sample_name+"_unmapped_r2.fastq.gz"))
    # print("r1_bam2fastq: ", r1_bam2fastq)
    # print("r2_bam2fastq: ", r2_bam2fastq)
    Step_2_check_bwa_subtraction_bedtools_bam2fastq = {}
    if r1_bam2fastq and r2_bam2fastq:
        url_r1_unmapped = os.path.join(url_root_bam2fastq, sample_name+"_unmapped_r1.fastq.gz")
        Step_2_check_bwa_subtraction_bedtools_bam2fastq["url_r1_unmapped"] = url_r1_unmapped

        url_r2_unmapped = os.path.join(url_root_bam2fastq, sample_name+"_unmapped_r2.fastq.gz")
        Step_2_check_bwa_subtraction_bedtools_bam2fastq["url_r2_unmapped"] = url_r2_unmapped
        return (True, Step_2_check_bwa_subtraction_bedtools_bam2fastq)
    else:
        return (False, Step_2_check_bwa_subtraction_bedtools_bam2fastq)






## Need to revise !!
def check_read_subtraction_bwa_align(sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Read_Subtraction", "bwa", "sam")
    print("bwa sam file: ", os.path.join(
        root_dir, sample_name+".sam"))
    bwa_read_subtraction_sam = os.path.exists(os.path.join(
        root_dir, sample_name+".sam"))
    print("bwa_read_subtraction_sam: ", bwa_read_subtraction_sam)
    if bwa_read_subtraction_sam:
        return True
    else:
        return False


def check_extract_non_host_reads_1(sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Extract_non_host_reads", "bam")
    print("bwa bam file: ", os.path.join(
        root_dir, sample_name+".bam"))
    extract_non_host_reads_1_bam = os.path.exists(os.path.join(
        root_dir, sample_name+".bam"))
    print("extract_non_host_reads_1_bam: ", extract_non_host_reads_1_bam)
    if extract_non_host_reads_1_bam:
        return True
    else:
        return False

def check_extract_non_host_reads_2(sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Extract_non_host_reads", "txt")
    print("bwa txt file: ", os.path.join(
        root_dir, sample_name+".txt"))
    extract_non_host_reads_2_txt = os.path.exists(os.path.join(
        root_dir, sample_name+".txt"))
    print("extract_non_host_reads_2_txt: ", extract_non_host_reads_2_txt)
    if extract_non_host_reads_2_txt:
        return True
    else:
        return False

def check_extract_non_host_reads_3(sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Extract_non_host_reads", "unmapped_bam")
    print("bwa unmapped_bam file: ", os.path.join(
        root_dir, sample_name+".unmapped.bam"))
    extract_non_host_reads_3_unmapped_bam = os.path.exists(os.path.join(
        root_dir, sample_name+".unmapped.bam"))
    print("extract_non_host_reads_3_unmapped_bam: ", extract_non_host_reads_3_unmapped_bam)
    if extract_non_host_reads_3_unmapped_bam:
        return True
    else:
        return False

def check_extract_non_host_reads_4(sample_datadir, sample_name):
    root_dir = os.path.join(sample_datadir, "Extract_non_host_reads", "unmapped_fastq")
    extract_non_host_reads_4_unmapped_fastq_r1 = os.path.exists(os.path.join(root_dir, sample_name+".unmapped.R1.fastq"))
    extract_non_host_reads_4_unmapped_fastq_r2 = os.path.exists(os.path.join(root_dir, sample_name+".unmapped.R2.fastq"))
    print("extract_non_host_reads_4_unmapped_fastq_r1: ", extract_non_host_reads_4_unmapped_fastq_r1)
    print("extract_non_host_reads_4_unmapped_fastq_r2: ", extract_non_host_reads_4_unmapped_fastq_r2)
    if extract_non_host_reads_4_unmapped_fastq_r1 and extract_non_host_reads_4_unmapped_fastq_r2:
        return True
    else:
        return False


def celery_check(project_name, email, analysis_code):
    new_task_id = project_name + email + analysis_code
    # while
    result = tasks.start_snakemake_task.AsyncResult(new_task_id)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print("@@@@@@@@@@@ task name : ", result)
    print("@@@@@@@@@@@ result.state: ", result.state)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    fetch_job_status = False
    if result.state == "PENDING":
        fetch_job_status = False
    elif result.state == "STARTED":
        fetch_job_status = True
    elif result.state == "SUCCESS":
        fetch_job_status = True
    elif result.state == "FAILURE":
        fetch_job_status = True
    elif result.state == "RETRY":
        fetch_job_status = True
    elif result.state == "REVOKED":
        fetch_job_status = True

    return result.state

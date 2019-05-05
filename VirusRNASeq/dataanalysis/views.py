from django.core.cache import cache
from django.http import HttpResponse
import json
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.views.generic.detail import DetailView
from django.conf import settings
from django.urls import reverse
import django_q
from django_q.tasks import async_task, result, fetch
from django_q.tasks import AsyncTask
from django_q.monitor import Stat
import math

import yaml
from django.core.files import File
import glob
import os
import shutil
import re
import subprocess
import json

from .forms import DataForm
from .models import Data


from django.utils import timezone
from dataanalysis.models import Document, PairedEnd, SingleEnd
from dataanalysis.forms import DocumentForm, PairedEndForm, SingleEndForm

from . import utils_func
from . import utils_func_reference_check_whole

TMP_DIR = "/home/kuan-hao/Documents/bioinformatics/Virus/analysis_results/tmp_project"


### Change QC directory !!!!


# Creating GET and POST functions!! When we access page, we are going to
# show the user a list of uploaded files

class BasicUploadView(DetailView):
    template_name = 'dataanalysis/data_upload.html'
    def get(self, request, slug_project):
        one_group_samples_csv = "/media/example_files/samples_csv/one"
        two_group_samples_csv = "/media/example_files/samples_csv/two"
        fastq_R1 = "/media/example_files/fastq_r1_r2/SRR8698485.R1.fastq.gz"
        fastq_R2 = "/media/example_files/fastq_r1_r2/SRR8698485.R2.fastq.gz"
        (project_name, analysis_code, email, assembly_type_input) = (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)

        # The base directory of the created project.
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        # The url for the slug_project
        url_parameter = project_name + '_' + email.split("@")[0]
        # Start checking files !!!
        # For sample name!
        (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)
        check_uploaded_fastq_file_ans = utils_func.check_uploaded_fastq_file(project_name, email, analysis_code)
        check_uploaded_fastq_file_whole_ans = utils_func.check_uploaded_fastq_file_whole_answer(check_uploaded_fastq_file_ans)
        uploaded_sample_file_url = utils_func.get_sample_file_url(project_name, email, analysis_code)
        return render(self.request, "dataanalysis/file_upload.html", {
            'project_name': project_name,
            'analysis_code': analysis_code,
            'email': email,
            'assembly_type_input': assembly_type_input,
            'samples_txt_file_name': samples_txt_file_name,
            'samples_list_key': samples_list_key,
            'sample_list': sample_list,
            'sample_file_validity': sample_file_validity,
            'sample_file_two_or_one': sample_file_two_or_one,
            'check_uploaded_fastq_file_ans': check_uploaded_fastq_file_ans,
            'check_uploaded_fastq_file_whole_ans': check_uploaded_fastq_file_whole_ans,
            'uploaded_sample_file_url': uploaded_sample_file_url,
            'one_group_samples_csv': one_group_samples_csv,
            'two_group_samples_csv': two_group_samples_csv,
            'fastq_R1': fastq_R1,
            'fastq_R2': fastq_R2,
        })

    def post(self, request, slug_project):
        one_group_samples_csv = "/media/samples.csv_example/one/samples.csv"
        two_group_samples_csv = "/media/samples.csv_example/two/samples.csv"
        fastq_R1 = "/media/example_files/fastq_r1_r2/SRR8698485.R1.fastq.gz"
        fastq_R2 = "/media/example_files/fastq_r1_r2/SRR8698485.R2.fastq.gz"
        (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
        # The base directory of the created project.
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        url_parameter = project_name + '_' + email.split("@")[0]
        (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)
        if assembly_type_input == "de_novo_assembly":
            template_html = "dataanalysis/analysis_home_denovo.html"
        elif assembly_type_input == "reference_based_assembly":
            template_html = "dataanalysis/analysis_home_reference_based.html"
        check_uploaded_fastq_file_ans = utils_func.check_uploaded_fastq_file(project_name, email, analysis_code)
        check_uploaded_fastq_file_whole_ans = utils_func.check_uploaded_fastq_file_whole_answer(check_uploaded_fastq_file_ans)
        uploaded_sample_file_url = utils_func.get_sample_file_url(project_name, email, analysis_code)
        ######################
        ## multi sample section
        if 'samples-files-upload' in request.POST:
            print("samples-files-upload!!!")
            myfile = request.FILES['samples-files-selected']
            print("myfile.name: ", myfile.name)
            fs = FileSystemStorage()
            if os.path.exists(os.path.join(base_dir, myfile.name)):
                os.remove(os.path.join(base_dir, myfile.name))
            filename = fs.save(os.path.join(base_dir, myfile.name), myfile)
            # Start checking files
            (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)
            check_uploaded_fastq_file_ans = utils_func.check_uploaded_fastq_file(project_name, email, analysis_code)
            check_uploaded_fastq_file_whole_ans = utils_func.check_uploaded_fastq_file_whole_answer(check_uploaded_fastq_file_ans)
            # Url needs to be updated one file is uploaded!!
            uploaded_sample_file_url = utils_func.get_sample_file_url(project_name, email, analysis_code)
            return render(request, "dataanalysis/file_upload.html", {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
                'sample_list': sample_list,
                'sample_file_validity': sample_file_validity,
                'sample_file_two_or_one': sample_file_two_or_one,
                'check_uploaded_fastq_file_ans': check_uploaded_fastq_file_ans,
                'check_uploaded_fastq_file_whole_ans': check_uploaded_fastq_file_whole_ans,
                'uploaded_sample_file_url': uploaded_sample_file_url,
                'one_group_samples_csv': one_group_samples_csv,
                'two_group_samples_csv': two_group_samples_csv,
                'fastq_R1': fastq_R1,
                'fastq_R2': fastq_R2,
            })
        elif 'remove-samples-file' in request.POST:
            print("remove-samples-file!!!")
            fs = FileSystemStorage()
            if fs.exists(base_dir):
                shutil.rmtree(base_dir)
            destination_QC_html_dir = os.path.join(os.path.dirname(__file__), 'templates', 'dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code)
            if os.path.exists(destination_QC_html_dir):
                shutil.rmtree(destination_QC_html_dir)
            # Start checking files
            (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)
            check_uploaded_fastq_file_ans = utils_func.check_uploaded_fastq_file(project_name, email, analysis_code)
            check_uploaded_fastq_file_whole_ans = utils_func.check_uploaded_fastq_file_whole_answer(check_uploaded_fastq_file_ans)
            uploaded_sample_file_url = utils_func.get_sample_file_url(project_name, email, analysis_code)
            return render(request, "dataanalysis/file_upload.html", {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
                'sample_list': sample_list,
                'sample_file_validity': sample_file_validity,
                'sample_file_two_or_one': sample_file_two_or_one,
                'check_uploaded_fastq_file_ans': check_uploaded_fastq_file_ans,
                'check_uploaded_fastq_file_whole_ans': check_uploaded_fastq_file_whole_ans,
                'uploaded_sample_file_url': uploaded_sample_file_url,
                'one_group_samples_csv': one_group_samples_csv,
                'two_group_samples_csv': two_group_samples_csv,
                'fastq_R1': fastq_R1,
                'fastq_R2': fastq_R2,
            })
        elif 'multi_samples_workflow_setup_button' in request.POST:
            (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)
            # if assembly_type_input
            if assembly_type_input == "de_novo_assembly":
                template_html = "dataanalysis/analysis_home_denovo.html"
                return redirect((reverse('de_novo_assembly_dataanalysis_home', kwargs={
                    'slug_project': url_parameter})))
            elif assembly_type_input == "reference_based_assembly":
                template_html = "dataanalysis/analysis_home_reference_based.html"
                return redirect((reverse('reference_mapping_dataanalysis_home', kwargs={
                    'slug_project': url_parameter})))
            return render(request, template_html, {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
                'sample_list': sample_list,
                'sample_file_validity': sample_file_validity,
                'sample_file_two_or_one': sample_file_two_or_one,
                'check_uploaded_fastq_file_ans': check_uploaded_fastq_file_ans,
                'check_uploaded_fastq_file_whole_ans': check_uploaded_fastq_file_whole_ans,
                'uploaded_sample_file_url': uploaded_sample_file_url,
                'one_group_samples_csv': one_group_samples_csv,
                'two_group_samples_csv': two_group_samples_csv,
                'fastq_R1': fastq_R1,
                'fastq_R2': fastq_R2,
            })
        myfile = request.FILES['file_choose']
        fs = FileSystemStorage()
        print("myfilemyfilemyfile: ", myfile)
        # Sample name!
        (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)
        for sample in sample_list:
            if not fs.exists(os.path.join(base_dir, 'Uploaded_files', sample)):
                os.makedirs(os.path.join(base_dir, 'Uploaded_files', sample))
                # Found split sample name
            file_name_tmp_1 = myfile.name.replace(".R1.fastq.gz", "")
            file_name_tmp_2 = file_name_tmp_1.replace(".R2.fastq.gz", "")
            if file_name_tmp_2 == sample:
                filename = fs.save(os.path.join(base_dir, "Uploaded_files", sample, myfile.name), myfile)
                uploaded_file_url = fs.url(filename)
        check_uploaded_fastq_file_ans = utils_func.check_uploaded_fastq_file(project_name, email, analysis_code)
        check_uploaded_fastq_file_whole_ans = utils_func.check_uploaded_fastq_file_whole_answer(check_uploaded_fastq_file_ans)
        data = {
            'project_name': project_name,
            'analysis_code': analysis_code,
            'email': email,
            'assembly_type_input': assembly_type_input,
            'samples_txt_file_name': samples_txt_file_name,
            'samples_list_key': samples_list_key,
            'sample_list': sample_list,
            'sample_file_validity': sample_file_validity,
            'sample_file_two_or_one': sample_file_two_or_one,
            'check_uploaded_fastq_file_ans': check_uploaded_fastq_file_ans,
            'check_uploaded_fastq_file_whole_ans': check_uploaded_fastq_file_whole_ans,
            'uploaded_sample_file_url': uploaded_sample_file_url,
            'one_group_samples_csv': one_group_samples_csv,
            'two_group_samples_csv': two_group_samples_csv,
            'fastq_R1': fastq_R1,
            'fastq_R2': fastq_R2,
            }
        return JsonResponse(data)



def reference_mapping_whole_dataanalysis(request, slug_project):
    ## Check if file exist !!
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    if assembly_type_input == "de_novo_assembly":
        template_html = "dataanalysis/analysis_home_denovo.html"
    elif assembly_type_input == "reference_based_assembly":
        template_html = "dataanalysis/analysis_home_reference_based.html"
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)
    url_base_dir = os.path.join('/media', 'tmp', project_name + '_' + email + '_' + analysis_code)
    # Check all the files are valid !!! (for referenced-based workflow)
    (overall_sample_result_checker, samples_all_info) = utils_func_reference_check_whole.Whole_check_reference_based_results(url_base_dir, base_dir, sample_list)
    fetch_job_success = utils_func_reference_check_whole.django_q_check(project_name, email, analysis_code)
    # If all checker is true ==> just jump to the current status page and then jump to new final overview page!!!!!!! and fetch_job.success
    if overall_sample_result_checker and fetch_job_success:
        return redirect((reverse('reference_mapping_dataanalysis_result_current_status', kwargs={
            'slug_project': url_parameter})))
    if request.method == 'POST' :
        if 'start-analysis-reference-based' in request.POST:
            upload_files_dir = os.path.join(base_dir, "Uploaded_files")
            prefix_dir = "/ssd/Howard/Virus/"
            tool_dir = os.path.join(prefix_dir, "tools")
            host_ref_dir = os.path.join(prefix_dir, "host_ref")
            pathogen_dir = os.path.join(prefix_dir, "pathogen")
            # Here is for creating directory!
            utils_func.create_sample_directory(project_name, email, analysis_code, sample_list)
            utils_func.create_time_directory(project_name, email, analysis_code)
            ### Fastqc
            fastqc_command = os.path.join(tool_dir, "FastQC", "fastqc")
            ### Trimmomatics
            trimmomatic_jar = os.path.join(tool_dir, "Trimmomatic/trimmomatic-0.38.jar")
            trimmomatic_threads = 8
            trimmomatic_phred = "-phred33"
            trimmomatic_select_adapter = request.POST.get('trimmomatic_illuminaclip')
            trimmomatic_adapter = os.path.join(prefix_dir, "tools/Trimmomatic/adapters", trimmomatic_select_adapter)
            trimmomatic_adapter_param = ":2:30:10"
            if trimmomatic_select_adapter == "None":
                trimmomatic_adapter = ""
                trimmomatic_adapter_param = ""
                trimmomatic_adapter_snakemake_variable = " "
            else:
                trimmomatic_adapter_snakemake_variable = "ILLUMINACLIP:" + trimmomatic_adapter + trimmomatic_adapter_param
            trimmomatic_leading = request.POST.get('trimmomatic_leading_quality')
            trimmomatic_trailing = request.POST.get('trimmomatic_trailing_quality')
            trimmomatic_minlen = request.POST.get('trimmomatic_minlen')
            trimmomatic_window_size = request.POST.get('trimmomatic_slidingwindow_size')
            trimmomatic_window_quality = request.POST.get('trimmomatic_slidingwindow_quality')

            ### BWA
            species_dir = "homo_sapiens"
            bwa_species = "homo_sapiens.fa"
            bwa_host_ref = os.path.join(host_ref_dir, species_dir, bwa_species)
            bwa_pathogen= request.POST.get('reads_alignment_reference')
            bwa_pathogen_full_name = ""
            bwa_pathogen_fastq = ""
            print("bwa_pathogenbwa_pathogen: ", bwa_pathogen)
            if bwa_pathogen == "TB":
                bwa_pathogen_full_name = "Mycobacterium_tuberculosis_H37Rv"
                bwa_pathogen_fastq = "Mycobacterium_tuberculosis_H37Rv.fna"
            bwa_pathogen_dir = os.path.join(pathogen_dir, bwa_pathogen_full_name, bwa_pathogen_fastq)
            bwa_threads = 10

            ### snpEff
            snpEff_jar = os.path.join(tool_dir, "snpEff/snpEff/snpEff.jar")
            snpEff_config = os.path.join(tool_dir, "snpEff/snpEff/snpEff.config")

            ### gatk
            gatk_jar = os.path.join(tool_dir, "gatk/gatk-package-4.1.0.0-local.jar")
            gatk_pathogen_dict = os.path.join(pathogen_dir, bwa_pathogen_full_name)

            config_file_path = os.path.join(base_dir, 'config.yaml')
            if assembly_type_input == "de_novo_assembly":
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_de_novo")
            elif assembly_type_input == "reference_based_assembly":
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_reference_based")
            destination_snakemake_file = os.path.join(base_dir, 'Snakefile')
            data = dict(
                assembly_type_input = assembly_type_input,
                samples_list_key = samples_list_key,
                project_name = project_name,
                datadir = base_dir,
                bwa_pathogen_full_name = bwa_pathogen_full_name,
                fastqc = dict(
                    fastqc_command = fastqc_command,
                ),
                trimmomatic = dict(
                    trimmomatic_jar = trimmomatic_jar,
                    trimmomatic_threads = trimmomatic_threads,
                    trimmomatic_phred = trimmomatic_phred,
                    trimmomatic_adapter = trimmomatic_adapter,
                    trimmomatic_adapter_param = trimmomatic_adapter_param,
                    trimmomatic_adapter_snakemake_variable = trimmomatic_adapter_snakemake_variable,
                    trimmomatic_window_size = trimmomatic_window_size,
                    trimmomatic_window_quality = trimmomatic_window_quality,
                    trimmomatic_leading = trimmomatic_leading,
                    trimmomatic_trailing = trimmomatic_trailing,
                    trimmomatic_minlen = trimmomatic_minlen,
                ),
                bwa = dict(
                    bwa_host_ref = bwa_host_ref,
                    bwa_pathogen = bwa_pathogen,
                    bwa_pathogen_dir = bwa_pathogen_dir,
                    bwa_threads = bwa_threads,
                ),
                snpEff = dict(
                    snpEff_jar = snpEff_jar,
                    snpEff_config = snpEff_config,
                ),
                gatk = dict(
                    gatk_jar = gatk_jar,
                    gatk_pathogen_dict = gatk_pathogen_dict,
                ),
            )
            with open(config_file_path, 'w') as ymlfile:
                yaml.dump(data, ymlfile, default_flow_style=False)
            shutil.copyfile(snakemake_file, destination_snakemake_file)
            if (not os.path.exists(os.path.join(base_dir, 'get_time_script'))):
                os.mkdir((os.path.join(base_dir, 'get_time_script')))
            for name in ['start', 'end']:
                get_time_script = os.path.join(
                    prefix_dir, "VirusRNASeq/VirusRNASeq/get_time_script/get_" + name + "_time.py")
                destination_get_time_script = os.path.join(
                    base_dir, 'get_time_script/get_' + name + '_time.py')
                shutil.copyfile(get_time_script, destination_get_time_script)

            new_task_name = project_name + email + analysis_code
            fetch_job = fetch(project_name + email + analysis_code)
            print("fetch_job: ", fetch_job)
            opts = {'group': assembly_type_input,
                    'task_name': new_task_name}

            for stat in Stat.get_all():
                print("@@@@@@@@@@@@ Get the status of all task")
                print(stat.cluster_id, stat.status)

            # Check the project!!
            if fetch_job is None:
                print("@@@@@@@@@@@@ Start running job: ")
                task_id = async_task(subprocess.call, ['snakemake'], shell=True, cwd=base_dir, q_options=opts)
                # task_id = async_task(math.copysign, 2, -2, q_options=opts)
            else:
                # The task is created so it won't be run again!
                print("@@@@@@@@@@@@ Project is submitted and created!!")
                # subprocess.call(['snakemake'], shell=True, cwd=base_dir)
                fetch_job = fetch(project_name + email + analysis_code)
                print("fetch_job: ", fetch_job)
                print("fetch_job.id: ", fetch_job.id)
                print("fetch_job.name: ", fetch_job.name)
                print("fetch_job.func: ", fetch_job.func)
                print("fetch_job.hook: ", fetch_job.hook)
                print("fetch_job.kwargs: ", fetch_job.kwargs)
                print("fetch_job.result: ", fetch_job.result)
                print("fetch_job.started: ", fetch_job.started)
                print("fetch_job.stopped: ", fetch_job.stopped)
                print("fetch_job.success: ", fetch_job.success)
                if fetch_job.success is False:
                    # The task is created and failed !! DO HERE!!!~~
                    pass
                else:
                    # The task is created successfully!!
                    pass

            template_html = "dataanalysis/analysis_home_reference_based.html"
            return redirect((reverse('reference_mapping_dataanalysis_result_current_status', kwargs={
                'slug_project': url_parameter})))

    return render(request, template_html, {
        'project_name': project_name,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'samples_txt_file_name': samples_txt_file_name,
        'samples_list_key': samples_list_key,
        'sample_list': sample_list
    })


def reference_mapping_current_status(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    url_base_dir = os.path.join('/media', 'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)
    # Get submission time
    submission_time_strip = 'no submission time'
    start_time_strip = 'no start time'
    end_time_strip = 'no end time'
    # Getting time!!
    submission_time_strip = utils_func.get_submission_time(project_name, email, analysis_code)
    start_time_strip = utils_func.get_start_time(project_name, email, analysis_code)
    end_time_strip = utils_func.get_end_time(project_name, email, analysis_code)
    url_parameter = project_name + '_' + email.split("@")[0]

    check_first_qc_ans_dict = {}
    check_trimming_qc_ans_dict = {}
    check_second_qc_ans_dict = {}
    check_read_subtraction_bwa_align_ans_dict = {}
    check_extract_non_host_reads_1_ans_dict = {}
    check_extract_non_host_reads_2_ans_dict = {}
    check_extract_non_host_reads_3_ans_dict = {}
    check_extract_non_host_reads_4_ans_dict = {}

    ##########
    ## THis is for the button to go to overview page ##
    ##########

    # if models.NewsletterUser.objects.filter(project_name=instance.project_name,email=instance.email, analysis_code=instance.analysis_code).exists():
    print("Failedtasks:: ", fetch("Project203d722859a511e9996fe41f1345dc74b05901180@ntu.edu.tw273e459859a511e9996fe41f1345dc74"))
    print("Resittdsafadfa:: ", result("f"))
    print("Resittdsafadfa:: ", result("d2aff0a9164c4c9abc17f4ffc037f21e"))
    print("Resittdsafadfa:: ", result("Project203d722859a511e9996fe41f1345dc74b05901180@ntu.edu.tw273e459859a511e9996fe41f1345dc74"))

    print("Stat number: ", Stat.get_all())
    for stat in Stat.get_all():
        print("@@@@@@@@@@@@@@@@@@@@stat:", stat)
        print("@@@@@@@@@@@@@@@@@@@@stat.cluster_id:", stat.cluster_id)
        print("@@@@@@@@@@@@@@@@@@@@stat.tob:", stat.tob)
        print("@@@@@@@@@@@@@@@@@@@@stat.uptime():", stat.uptime())
        print("@@@@@@@@@@@@@@@@@@@@stat.reincarnations:", stat.reincarnations)
        print("@@@@@@@@@@@@@@@@@@@@stat.status:", stat.status)
        print("@@@@@@@@@@@@@@@@@@@@stat.task_q_size:", stat.task_q_size)
        print("@@@@@@@@@@@@@@@@@@@@stat.done_q_size:", stat.done_q_size)
        print("@@@@@@@@@@@@@@@@@@@@stat.pusher:", stat.pusher)
        print("@@@@@@@@@@@@@@@@@@@@stat.monitor:", stat.monitor)
        print("@@@@@@@@@@@@@@@@@@@@stat.sentinel:", stat.sentinel)
        print("@@@@@@@@@@@@@@@@@@@@stat.workers:", stat.workers)
        print("@@@@@@@@@@@@@@@@@@@@stat.empty_queues:", stat.empty_queues)
        print("@@@@@@@@@@@@@@@@@@@@stat.pusher:", stat.pusher)


    # django_q.































    if request.method == 'POST':
        if 'go-to-overview-button' in request.POST:
            return redirect((reverse('reference_mapping_dataanalysis_result_current_status', kwargs={
                'slug_project': url_parameter})))

    (overall_sample_result_checker, samples_all_info) = utils_func_reference_check_whole.Whole_check_reference_based_results(url_base_dir, base_dir, sample_list)
    fetch_job_success = utils_func_reference_check_whole.django_q_check(project_name, email, analysis_code)
    # print("overall_sample_result_checker", overall_sample_result_checker)
    # print("fetch_job_success", fetch_job_success)
    if overall_sample_result_checker and fetch_job_success:
        return redirect((reverse('reference_mapping_dataanalysis_result_overview', kwargs={
            'slug_project': url_parameter})))

    return render(request, "dataanalysis/analysis_result_status_reference_based.html", {
        'project_name': project_name,
        'email': email,
        'analysis_code': analysis_code,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
        'samples_all_info': samples_all_info,
        # Here, the variable need to be removed

        'submission_time': submission_time_strip,

        "samples_txt_file_name": samples_txt_file_name,
        "samples_list_key": samples_list_key,
        "sample_list": sample_list,
    })

def reference_mapping_show_result_overview(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    url_base_dir = os.path.join('/media', 'tmp', project_name + '_' + email + '_' + analysis_code)
    # Get sample name
    (samples_txt_file_name, samples_list_key, sample_list, sample_file_validity, sample_file_two_or_one) = utils_func.check_samples_txt_file(base_dir)

    # Getting time!!
    submission_time_strip = utils_func.get_submission_time(project_name, email, analysis_code)
    start_time_strip = utils_func.get_start_time(project_name, email, analysis_code)
    end_time_strip = utils_func.get_end_time(project_name, email, analysis_code)

    samples_all_result = {}
    for sample_name in sample_list:
        url_sample_base_dir = os.path.join(url_base_dir, sample_name)
        sample_datadir = os.path.join(base_dir, sample_name)
        samples_all_result[sample_name] = {}
        one_sample_all_result = {}
        qc_datadir = os.path.join(base_dir, sample_name, 'Step_1', 'QC')
        # Html files that would be copied
        fastqc_datadir_pre_r1 = os.path.join(qc_datadir, 'pre', sample_name+'.R1_fastqc.html')
        fastqc_datadir_pre_r2 = os.path.join(
            qc_datadir, 'pre', sample_name+'.R2_fastqc.html')
        multiqc_datadir_pre = os.path.join(
            qc_datadir, 'pre', sample_name+'_multiqc.html')

        fastqc_datadir_post_r1 = os.path.join(
            qc_datadir, 'post', sample_name+'_r1_paired_fastqc.html')
        fastqc_datadir_post_r2 = os.path.join(
            qc_datadir, 'post', sample_name+'_r2_paired_fastqc.html')
        multiqc_datadir_post = os.path.join(
            qc_datadir, 'post', sample_name+'_multiqc.html')

        snpeff_html_datadir = os.path.join(
            base_dir, sample_name, 'Step_5', 'snpeff', sample_name+'_snpEff_summary.html')
        # Destination of html file
        destination_QC_html_dir = os.path.join(os.path.dirname(__file__), 'templates', 'dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, '', sample_name, 'Step_1', 'QC')
        destination_snpeff_html_dir = os.path.join(os.path.dirname(__file__), 'templates', 'dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, '', sample_name, 'Step_5', 'snpeff')
        destination_fastqc_datadir_pre_r1 = os.path.join(destination_QC_html_dir, 'pre', sample_name+'.R1_fastqc.html')
        destination_fastqc_datadir_pre_r2 = os.path.join(destination_QC_html_dir, 'pre', sample_name+'.R2_fastqc.html')
        destination_multiqc_datadir_pre = os.path.join(destination_QC_html_dir, 'pre', sample_name+'_multiqc.html')
        destination_fastqc_datadir_post_r1 = os.path.join(destination_QC_html_dir, 'post', sample_name+'_r1_paired_fastqc.html')
        destination_fastqc_datadir_post_r2 = os.path.join(destination_QC_html_dir, 'post', sample_name+'_r2_paired_fastqc.html')
        destination_multiqc_datadir_post = os.path.join(destination_QC_html_dir, 'post', sample_name+'_multiqc.html')
        destination_snpeff_datadir = os.path.join(destination_snpeff_html_dir, sample_name+'_snpEff_summary.html')

        if not os.path.exists(destination_QC_html_dir):
            os.makedirs(destination_QC_html_dir)
            os.makedirs(os.path.join(destination_QC_html_dir, 'pre'))
            os.makedirs(os.path.join(destination_QC_html_dir, 'post'))
            shutil.copyfile(fastqc_datadir_pre_r1, destination_fastqc_datadir_pre_r1)
            shutil.copyfile(fastqc_datadir_pre_r2, destination_fastqc_datadir_pre_r2)
            shutil.copyfile(multiqc_datadir_pre, destination_multiqc_datadir_pre)
            shutil.copyfile(fastqc_datadir_post_r1, destination_fastqc_datadir_post_r1)
            shutil.copyfile(fastqc_datadir_post_r2, destination_fastqc_datadir_post_r2)
            shutil.copyfile(multiqc_datadir_post, destination_multiqc_datadir_post)
        if not os.path.exists(destination_snpeff_html_dir):
            os.makedirs(destination_snpeff_html_dir)
            shutil.copyfile(snpeff_html_datadir, destination_snpeff_datadir)
        one_sample_all_result["fastqc_datadir_pre_r1"] = sample_name+'.R1_fastqc.html'
        one_sample_all_result["fastqc_datadir_pre_r2"] = sample_name+'.R2_fastqc.html'
        one_sample_all_result["multiqc_datadir_pre"] = sample_name+'_multiqc.html'
        one_sample_all_result["fastqc_datadir_post_r1"] = sample_name+'_r1_paired_fastqc.html'
        one_sample_all_result["fastqc_datadir_post_r2"] = sample_name+'_r2_paired_fastqc.html'
        one_sample_all_result["multiqc_datadir_post"] = sample_name+'_multiqc.html'
        Step_1_check_first_qc = utils_func.Step_1_check_first_qc(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_1_check_first_qc"] = Step_1_check_first_qc[1]
        Step_1_check_trimming_qc = utils_func.Step_1_check_trimming_qc(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_1_check_trimming_qc"] = Step_1_check_trimming_qc[1]
        Step_1_check_second_qc = utils_func.Step_1_check_second_qc(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_1_check_second_qc"] = Step_1_check_second_qc[1]
        Step_2_check_reference_based_bwa_sam = utils_func.Step_2_check_reference_based_bwa_sam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_2_check_reference_based_bwa_sam"] = Step_2_check_reference_based_bwa_sam[1]
        Step_2_check_reference_based_bwa_report_txt = utils_func.Step_2_check_reference_based_bwa_report_txt(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_2_check_reference_based_bwa_report_txt"] = Step_2_check_reference_based_bwa_report_txt[1]
        Step_3_check_reference_based_samtools_fixmate_bam = utils_func.Step_3_check_reference_based_samtools_fixmate_bam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_3_check_reference_based_samtools_fixmate_bam"] = Step_3_check_reference_based_samtools_fixmate_bam[1]
        Step_3_check_reference_based_samtools_sorted_bam = utils_func.Step_3_check_reference_based_samtools_sorted_bam(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_3_check_reference_based_samtools_sorted_bam"] = Step_3_check_reference_based_samtools_sorted_bam[1]
        Step_4_check_reference_based_bcftools_vcf = utils_func.Step_4_check_reference_based_bcftools_vcf(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_4_check_reference_based_bcftools_vcf"] = Step_4_check_reference_based_bcftools_vcf[1]
        Step_4_check_reference_based_bcftools_vcf_revise = utils_func.Step_4_check_reference_based_bcftools_vcf_revise(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_4_check_reference_based_bcftools_vcf_revise"] = Step_4_check_reference_based_bcftools_vcf_revise[1]
        Step_5_check_reference_based_snpeff_vcf_annotation = utils_func.Step_5_check_reference_based_snpeff_vcf_annotation(url_sample_base_dir, sample_datadir, sample_name)
        one_sample_all_result["Step_5_check_reference_based_snpeff_vcf_annotation"] = Step_5_check_reference_based_snpeff_vcf_annotation[1]
        samples_all_result[sample_name] = one_sample_all_result
        trimmomatic_command_log = os.path.join(settings.MEDIA_ROOT, 'tmp', project_name + '_' + email + '_' + analysis_code, sample_name, 'logs', 'trimmomatic_pe', sample_name+'.command.log')
        if os.path.exists(trimmomatic_command_log):
            f_trimmomatic_command_log = open(trimmomatic_command_log, "r")
            output_string = f_trimmomatic_command_log.readlines()
            tmp_1 = re.findall("[\:]\s+[0-9]*", output_string[-2])
            tmp_2 = ''.join(tmp_1)
            ans_list=tmp_2.split(': ')
            trimmo_intput_read_pairs = ans_list[1]
            one_sample_all_result["trimmo_intput_read_pairs"] = trimmo_intput_read_pairs
            trimmo_both_surviving = ans_list[2]
            one_sample_all_result["trimmo_both_surviving"] = trimmo_both_surviving
            trimmo_forward_only_surviving = ans_list[3]
            one_sample_all_result["trimmo_forward_only_surviving"] = trimmo_forward_only_surviving
            trimmo_reverse_only_surviving = ans_list[4]
            one_sample_all_result["trimmo_reverse_only_surviving"] = trimmo_reverse_only_surviving
            trimmo_dropped = ans_list[5]
            one_sample_all_result["trimmo_dropped"] = trimmo_dropped
        samples_all_result[sample_name] = one_sample_all_result
    print("one_sample_all_resultone_sample_all_result: ", samples_all_result)

    return render(request, "dataanalysis/analysis_result_overview_reference_based.html", {
        "project_name": project_name,
        "analysis_code": analysis_code,
        "email": email,
        "assembly_type_input": assembly_type_input,
        "submission_time": submission_time_strip,
        "start_time": start_time_strip,
        "end_time": end_time_strip,
        "url_parameter": url_parameter,
        "samples_all_result": samples_all_result,
        "samples_txt_file_name": samples_txt_file_name,
        "samples_list_key": samples_list_key,
        "sample_list": sample_list,
    })




def show_result(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    return render(request, "dataanalysis/analysis_result.html", {
        'project_name': project_name,
        'email': email,
        'assembly_type_input':assembly_type_input,
        'url_parameter': url_parameter,
    })


def pre_qc_html_view_multiqc(request, slug_project, slug_sample):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, slug_sample, 'Step_1', 'QC', 'pre', slug_sample+'_multiqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def pre_qc_html_view_r1(request, slug_project, slug_sample):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, slug_sample, 'Step_1', 'QC', 'pre', slug_sample+'.R1_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def pre_qc_html_view_r2(request, slug_project, slug_sample):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, slug_sample, 'Step_1', 'QC', 'pre', slug_sample+'.R2_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_multiqc(request, slug_project, slug_sample):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, slug_sample, 'Step_1', 'QC', 'post', slug_sample+'_multiqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_r1(request, slug_project, slug_sample):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, slug_sample, 'Step_1', 'QC', 'post', slug_sample+'_r1_paired_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_r2(request, slug_project, slug_sample):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, slug_sample, 'Step_1', 'QC', 'post', slug_sample+'_r2_paired_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def snpeff_report(request, slug_project, slug_sample):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, slug_sample, 'Step_5', 'snpeff', slug_sample+'_snpEff_summary.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

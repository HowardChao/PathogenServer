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

TMP_DIR = "/home/kuan-hao/Documents/bioinformatics/Virus/analysis_results/tmp_project"


### Change QC directory !!!!


# Creating GET and POST functions!! When we access page, we are going to
# show the user a list of uploaded files

class BasicUploadView(DetailView):
    template_name = 'dataanalysis/data_upload.html'
    def get(self, request, slug_project):
        (project_name, analysis_code, email, assembly_type_input) = (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
        # The base directory of the created project.
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        # The url for the slug_project
        url_parameter = project_name + '_' + email.split("@")[0]
        # Start checking files !!!
        # For sample name!
        (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
        data_list = utils_func.get_data_list(project_name, email, analysis_code)
        return render(self.request, "dataanalysis/file_upload.html", {
            'project_name': project_name,
            'analysis_code': analysis_code,
            'email': email,
            'assembly_type_input': assembly_type_input,
            'datas': data_list,
            'samples_txt_file_name': samples_txt_file_name,
            'samples_list_key': samples_list_key,
            'sample_list': sample_list,
        })

    def post(self, request, slug_project):
        (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
        url_parameter = project_name + '_' + email.split("@")[0]
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
        if assembly_type_input == "de_novo_assembly":
            template_html = "dataanalysis/analysis_home_denovo.html"
        elif assembly_type_input == "reference_based_assembly":
            template_html = "dataanalysis/analysis_home_reference_based.html"

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
            uploaded_file_url_se = fs.url(filename)
            # Start checking files
            (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
            ####################
            ### Need to modify!!
            ####################
            data_list = utils_func.get_data_list(project_name, email, analysis_code)
            return render(request, "dataanalysis/file_upload.html", {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'datas': data_list,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
                'sample_list': sample_list,
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
            (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
            data_list = utils_func.get_data_list(project_name, email, analysis_code)
            return render(request, "dataanalysis/file_upload.html", {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'datas': data_list,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
                'sample_list': sample_list,
            })
        elif 'multi_samples_workflow_setup_button' in request.POST:
            (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
            data_list = utils_func.get_data_list(project_name, email, analysis_code)
            return redirect((reverse('dataanalysis_home', kwargs={
                'slug_project': url_parameter})))
            return render(request, template_html, {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'datas': data_list,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
                'sample_list': sample_list,
            })
        myfile = request.FILES['file_choose']
        fs = FileSystemStorage()
        # Sample name!
        (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
        data_list = utils_func.get_data_list(project_name, email, analysis_code)
        sample_name = sample_list[0]
        # Removing files
        if not fs.exists(os.path.join(base_dir, 'Uploaded_files')):
            os.mkdir((os.path.join(base_dir, 'Uploaded_files')))
            if not fs.exists(os.path.join(base_dir, 'Uploaded_files', sample_name)):
                os.mkdir((os.path.join(base_dir, 'Uploaded_files', sample_name)))
                # Found split sample name
        filename = fs.save(os.path.join(base_dir, "Uploaded_files", sample_name, myfile.name), myfile)
        uploaded_file_url = fs.url(filename)
        data = {
            'project_name': project_name,
            'analysis_code': analysis_code,
            'email': email,
            'assembly_type_input': assembly_type_input,
            'name': myfile.name,
            'datas': data_list,
            'samples_txt_file_name': samples_txt_file_name,
            'samples_list_key': samples_list_key,
            'sample_list': sample_list
            }
        return JsonResponse(data)



def whole_dataanalysis(request, slug_project):
    ## Check if file exist !!
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    if assembly_type_input == "de_novo_assembly":
        template_html = "dataanalysis/analysis_home_denovo.html"
    elif assembly_type_input == "reference_based_assembly":
        template_html = "dataanalysis/analysis_home_reference_based.html"
    if request.method == 'POST' :
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        if 'start-analysis-de-novo' in request.POST:
            pass
        elif 'start-analysis-reference-based' in request.POST:
            upload_files_dir = os.path.join(base_dir, "Uploaded_files")
            prefix_dir = "/ssd/Howard/Virus/"
            tool_dir = os.path.join(prefix_dir, "tools")
            host_ref_dir = os.path.join(prefix_dir, "host_ref")
            pathogen_dir = os.path.join(prefix_dir, "pathogen")
            # Get sample names
            (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
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
            trimmomatic_leading = request.POST.get('trimmomatic_leading_quality')
            trimmomatic_trailing = request.POST.get('trimmomatic_trailing_quality')
            trimmomatic_minlen = request.POST.get('trimmomatic_minlen')
            trimmomatic_window_size = request.POST.get('trimmomatic_slidingwindow_size')
            trimmomatic_window_quality = request.POST.get('trimmomatic_slidingwindow_quality')

            ### BWA
            species_dir = "homo_sapiens"
            bwa_species = "homo_sapiens.fa"
            bwa_host_ref = os.path.join(host_ref_dir, species_dir, bwa_species)

            ### snpEff
            snpEff_jar = os.path.join(tool_dir, "snpEff/snpEff/snpEff.jar")

            ### gatk
            gatk_jar = os.path.join(tool_dir, "gatk/gatk-package-4.1.0.0-local.jar")

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
                fastqc = dict(
                    fastqc_command = fastqc_command,
                ),
                trimmomatic = dict(
                    trimmomatic_jar = trimmomatic_jar,
                    trimmomatic_threads = trimmomatic_threads,
                    trimmomatic_phred = trimmomatic_phred,
                    trimmomatic_adapter = trimmomatic_adapter,
                    trimmomatic_adapter_param = trimmomatic_adapter_param,
                    trimmomatic_window_size = trimmomatic_window_size,
                    trimmomatic_window_quality = trimmomatic_window_quality,
                    trimmomatic_leading = trimmomatic_leading,
                    trimmomatic_trailing = trimmomatic_trailing,
                    trimmomatic_minlen = trimmomatic_minlen,
                ),
                bwa = dict(
                    bwa_host_ref = bwa_host_ref,
                ),
                snpEff = dict(
                    snpEff_jar = snpEff_jar,
                ),
                gatk_jar = dict(
                    gatk_jar = gatk_jar,
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
            # subprocess.call(['snakemake'], shell=True, cwd=base_dir)
            return redirect((reverse('dataanalysis_result_current_status', kwargs={
                'slug_project': url_parameter})))

    return render(request, template_html, {
        'which': "normal",
        'project_name': project_name,
        'email': email,
        'assembly_type_input': assembly_type_input,
    })


def show_result_overview(request, slug_project):
    project_name = "No value"
    analysis_code = "No value"
    email = "No value"
    submission_time_strip = "No value"
    start_time_strip = "No value"
    end_time_strip = "No value"
    url_parameter = "No value"
    sample_name = "No value"
    trimmo_intput_read_pairs = "No value"
    trimmo_both_surviving = "No value"
    trimmo_forward_only_surviving = "No value"
    trimmo_reverse_only_surviving = "No value"
    trimmo_dropped = "No value"
    submission_time_strip = 'no submission time'
    start_time_strip = 'no start time'
    end_time_strip = 'no end time'

    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    # Get sample name
    (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
    sample_name = sample_list[0]

    # Getting time!!
    submission_time_strip = utils_func.get_submission_time(project_name, email, analysis_code)
    start_time_strip = utils_func.get_start_time(project_name, email, analysis_code)
    end_time_strip = utils_func.get_end_time(project_name, email, analysis_code)

    qc_datadir = os.path.join(base_dir, sample_name, 'Step_1', 'QC')
    # Set temporary sample_name
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

    destination_QC_html_dir = os.path.join(os.path.dirname(__file__), 'templates', 'dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, '', sample_name, 'Step_1', 'QC')
    destination_fastqc_datadir_pre_r1 = os.path.join(destination_QC_html_dir, 'pre', sample_name+'.R1_fastqc.html')
    destination_fastqc_datadir_pre_r2 = os.path.join(destination_QC_html_dir, 'pre', sample_name+'.R2_fastqc.html')
    destination_multiqc_datadir_pre = os.path.join(destination_QC_html_dir, 'pre', sample_name+'_multiqc.html')
    destination_fastqc_datadir_post_r1 = os.path.join(destination_QC_html_dir, 'post', sample_name+'_r1_paired_fastqc.html')
    destination_fastqc_datadir_post_r2 = os.path.join(destination_QC_html_dir, 'post', sample_name+'_r2_paired_fastqc.html')
    destination_multiqc_datadir_post = os.path.join(destination_QC_html_dir, 'post', sample_name+'_multiqc.html')
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


    trimmomatic_command_log = os.path.join(settings.MEDIA_ROOT, 'tmp', project_name + '_' + email + '_' + analysis_code, sample_name, 'logs', 'trimmomatic_pe', sample_name+'.command.log')
    if os.path.exists(trimmomatic_command_log):
        f_trimmomatic_command_log = open(trimmomatic_command_log, "r")
        output_string = f_trimmomatic_command_log.readlines()
        tmp_1 = re.findall("[\:]\s+[0-9]*", output_string[-2])
        tmp_2 = ''.join(tmp_1)
        ans_list=tmp_2.split(': ')
        trimmo_intput_read_pairs = ans_list[1]
        trimmo_both_surviving = ans_list[2]
        trimmo_forward_only_surviving = ans_list[3]
        trimmo_reverse_only_surviving = ans_list[4]
        trimmo_dropped = ans_list[5]
    return render(request, "dataanalysis/analysis_result_overview.html", {
        "project_name": project_name,
        "analysis_code": analysis_code,
        "email": email,
        "assembly_type_input": assembly_type_input,
        "submission_time": submission_time_strip,
        "start_time": start_time_strip,
        "end_time": end_time_strip,
        "url_parameter": url_parameter,
        "fastqc_datadir_pre_r1": sample_name+'.R1_fastqc.html',
        "fastqc_datadir_pre_r2": sample_name+'.R2_fastqc.html',
        "multiqc_datadir_pre": sample_name+'_multiqc.html',
        "fastqc_datadir_post_r1": sample_name+'_r1_paired_fastqc.html',
        "fastqc_datadir_post_r2": sample_name+'_r2_paired_fastqc.html',
        "multiqc_datadir_post": sample_name+'_multiqc.html',
        "trimmo_intput_read_pairs": trimmo_intput_read_pairs,
        "trimmo_both_surviving": trimmo_both_surviving,
        "trimmo_forward_only_surviving": trimmo_forward_only_surviving,
        "trimmo_reverse_only_surviving": trimmo_reverse_only_surviving,
        "trimmo_dropped": trimmo_dropped,
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

def current_status(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
    ##~~~
    sample_name = sample_list[0]

    # Get submission time
    submission_time_strip = 'no submission time'
    start_time_strip = 'no start time'
    end_time_strip = 'no end time'
    # Getting time!!
    submission_time_strip = utils_func.get_submission_time(project_name, email, analysis_code)
    start_time_strip = utils_func.get_start_time(project_name, email, analysis_code)
    end_time_strip = utils_func.get_end_time(project_name, email, analysis_code)
    url_parameter = project_name + '_' + email.split("@")[0]

    if ('view_counter_%s' % url_parameter) in request.session:
        view_counter = request.session['view_counter_%s' % url_parameter]
        view_counter = view_counter + 1
        request.session['view_counter_%s' % url_parameter] = view_counter
    else:
        view_counter = 1
        request.session['view_counter_%s' % url_parameter] = view_counter
    if request.method == 'POST':
        if 'go-to-overview-button' in request.POST:
            print("(((((()))))):", reverse('dataanalysis_result_overview', kwargs={
                'slug_project': url_parameter}))
            return redirect((reverse('dataanalysis_result_overview', kwargs={
                'slug_project': url_parameter})))
    sample_datadir = os.path.join(base_dir, sample_name)
    print("11111111111111", sample_datadir)
    files = os.listdir(os.path.join(sample_datadir))
    # Get current sample names
    url_parameter = project_name + '_' + email.split("@")[0]
    # Check the process of files
    check_submission_time_ans = False
    check_first_qc_ans = False
    check_trimming_qc_ans = False
    check_second_qc_ans = False
    check_read_subtraction_bwa_align_ans = False
    check_extract_non_host_reads_1_ans = False
    check_extract_non_host_reads_2_ans = False
    check_extract_non_host_reads_3_ans = False
    check_extract_non_host_reads_4_ans = False
    check_end_time_ans = False

    view_counter_end = "Not Start Counting"
    if utils_func.check_submission_time_file(sample_datadir, sample_name) is True:
        check_submission_time_ans = True
    if utils_func.check_first_qc(sample_datadir, sample_name) is True:
        check_first_qc_ans = True
    if utils_func.check_trimming_qc(sample_datadir, sample_name) is True:
        check_trimming_qc_ans = True
    if utils_func.check_second_qc(sample_datadir, sample_name) is True:
        check_second_qc_ans = True
    if utils_func.check_read_subtraction_bwa_align(sample_datadir, sample_name) is True:
        check_read_subtraction_bwa_align_ans = True
    if utils_func.check_extract_non_host_reads_1(sample_datadir, sample_name) is True:
        check_extract_non_host_reads_1_ans = True
    if utils_func.check_extract_non_host_reads_2(sample_datadir, sample_name) is True:
        check_extract_non_host_reads_2_ans = True
    if utils_func.check_extract_non_host_reads_3(sample_datadir, sample_name) is True:
        check_extract_non_host_reads_3_ans = True
    if utils_func.check_extract_non_host_reads_4(sample_datadir, sample_name) is True:
        check_extract_non_host_reads_4_ans = True
    if utils_func.check_end_time_file(sample_datadir, sample_name) is True:
        check_end_time_ans = True
    whole_file_check = check_first_qc_ans and check_trimming_qc_ans and check_second_qc_ans and check_read_subtraction_bwa_align_ans
    if ((view_counter is 1) or (check_submission_time_ans is False and check_first_qc_ans is False and check_trimming_qc_ans is False and check_second_qc_ans is False and check_read_subtraction_bwa_align_ans is False and check_end_time_ans is False) or submission_time_strip == 'no submission time'):
        print("(check_submission_time_ans is False and check_first_qc_ans is False and check_trimming_qc_ans is False and check_second_qc_ans is False and check_read_subtraction_bwa_align_ans is False and check_end_time_ans is False) or submission_time_strip == 'no submission time'): ",
        (check_submission_time_ans is False and check_first_qc_ans is False and check_trimming_qc_ans is False and check_second_qc_ans is False and check_read_subtraction_bwa_align_ans is False and check_end_time_ans is False) or submission_time_strip == 'no submission time')
        # This is the first time to run (with the submission time stamp)
        submission_time = timezone.now()
        submission_time_strip = submission_time.strftime("%B %d, %Y, %I:%M:%S %p")
        f_submission = open(submission_time_file, 'w')
        f_submission.writelines(submission_time_strip)
        f_submission.close()
        # request.session["submission_time"] = submission_time_strip
        subprocess.Popen(['snakemake', 'targets'], cwd=base_dir)
    print("check_first_qc_ans: ", check_first_qc_ans)
    print("check_trimming_qc_ans: ", check_trimming_qc_ans)
    print("check_second_qc_ans: ", check_second_qc_ans)
    print("check_read_subtraction_bwa_align_ans: ",
          check_read_subtraction_bwa_align_ans)
    return render(request, "dataanalysis/analysis_result_status.html", {
        'project_name': project_name,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
        'check_first_qc_ans': check_first_qc_ans,
        'check_trimming_qc_ans': check_trimming_qc_ans,
        'check_second_qc_ans': check_second_qc_ans,
        'check_read_subtraction_bwa_align_ans': check_read_subtraction_bwa_align_ans,
        'check_extract_non_host_reads_1_ans': check_extract_non_host_reads_1_ans,
        'check_extract_non_host_reads_2_ans': check_extract_non_host_reads_2_ans,
        'check_extract_non_host_reads_3_ans': check_extract_non_host_reads_3_ans,
        'check_extract_non_host_reads_4_ans': check_extract_non_host_reads_4_ans,
        'submission_time': submission_time_strip,
        'view_counter_end': view_counter_end,
        'view_counter': view_counter,
    })


def pre_qc_html_view_multiqc(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
    ##~~~
    sample_name = sample_list[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, sample_name, 'Step_1', 'QC', 'pre', sample_name+'_multiqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def pre_qc_html_view_r1(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
    ##~~~
    sample_name = sample_list[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, sample_name, 'Step_1', 'QC', 'pre', sample_name+'.R1_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def pre_qc_html_view_r2(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
    ##~~~
    sample_name = sample_list[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, sample_name, 'Step_1', 'QC', 'pre', sample_name+'.R2_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_multiqc(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
    ##~~~
    sample_name = sample_list[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, sample_name, 'Step_1', 'QC', 'post', sample_name+'_multiqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_r1(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
    ##~~~
    sample_name = sample_list[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, sample_name, 'Step_1', 'QC', 'post', sample_name+'_r1_paired_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_r2(request, slug_project):
    (project_name, analysis_code, email, assembly_type_input) = utils_func.check_session(request)
    url_parameter = project_name + '_' + email.split("@")[0]
    base_dir = os.path.join(settings.MEDIA_ROOT,
                            'tmp', project_name + '_' + email + '_' + analysis_code)
    (samples_txt_file_name, samples_list_key, sample_list) = utils_func.check_samples_txt_file(base_dir)
    ##~~~
    sample_name = sample_list[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, sample_name, 'Step_1', 'QC', 'post', sample_name+'_r2_paired_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

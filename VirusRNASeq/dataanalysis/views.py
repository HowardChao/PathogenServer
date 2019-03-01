from django.core.cache import cache
from django.http import HttpResponse
import json
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.conf import settings
from django.urls import reverse
import yaml
from django.core.files import File
import glob
import os
import shutil
import re
import subprocess
from django.utils import timezone

from dataanalysis.models import Document, PairedEnd, SingleEnd
from dataanalysis.forms import DocumentForm, PairedEndForm, SingleEndForm

from . import utils_func

TMP_DIR = "/home/kuan-hao/Documents/bioinformatics/Virus/analysis_results/tmp_project"

# Creating GET and POST functions!! When we access page, we are going to
# show the user a list of uploaded files
class BasicUploadView(View):
    def get(self, request):
        files_list = Document.objects.all()
        context = {
            "files": files_list,
        }
        return render(self.request, 'dataanalysis/home.html', context=context)

    def post(self, request):
        form = DocumentForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            getfile = form.save()
            data = {'is_valid': True,
                    'name': getfile.document.name, 'url': getfile.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)

def data_analysis_home(request):

    if request.method == 'POST' and request.FILES['myfile1']:
        project_name = "None"
        analysis_code = "None"
        # upload_dir = os.path.join(TMP_DIR, tmp_project_id, "reads")
        # print("upload_dir id: ", upload_dir)
        # if not os.path.exists(upload_dir):
        #     os.makedirs(upload_dir)
        myfile = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        filename2 = fs.save(myfile2.name, myfile2)
        uploaded_file_url = fs.url(filename)
        uploaded_file_url2 = fs.url(filename2)
        return render(request, 'dataanalysis/home.html', {
            'uploaded_file_url': uploaded_file_url,
            'uploaded_file_url2': uploaded_file_url2,
        })
    return render(request, 'dataanalysis/home.html')
    # documents = Document.objects.all()
    # return render(request, 'dataanalysis/home.html', { 'documents': documents })


def whole_dataanalysis(request, slug_project):
    print("Inside data_analysis_home !!!")

    ## Check if file exist !!
    # os.listdir(settings)
    uploaded_file_url_pe_1 = None
    uploaded_file_url_pe_2 = None
    uploaded_file_url_se = None
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
    (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se) = Check_Uploaded_File_Name(
        project_name, email, analysis_code)
    url_parameter = project_name + '_' + email.split("@")[0]
    if request.method == 'POST' :
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        if 'upload-paired-end-file' in request.POST:
            print("    * Inside upload-paired-end-file")
            myfile1 = request.FILES['r1']
            myfile2 = request.FILES['r2']
            fs = FileSystemStorage()
            print("Checker path: ", os.path.join(base_dir, 'pe'))
            print("Checker path: ", os.path.join(base_dir, 'se'))
            if fs.exists(os.path.join(base_dir, 'pe')):
                print("Removing files")
                shutil.rmtree(os.path.join(base_dir, "pe"))
            if fs.exists(os.path.join(base_dir, "se")):
                print("Removing files")
                shutil.rmtree(os.path.join(base_dir, "se"))
            ## Found split sample name
            sample_name = os.path.splitext(os.path.splitext(
                os.path.splitext(myfile1.name)[0])[0])[0]
            request.session["sample_name"] = sample_name
            print("pe_sample_name: ", sample_name)
            request.session["se_or_pe"] = "pe"
            print("se_or_pe: ", "pe")
            filename1 = fs.save(os.path.join(base_dir, "pe", myfile1.name), myfile1)
            filename2 = fs.save(os.path.join(base_dir, "pe", myfile2.name), myfile2)
            uploaded_file_url_pe_1 = fs.url(filename1)
            uploaded_file_url_pe_2 = fs.url(filename2)
            print("uploaded_file_url_pe_1: ", uploaded_file_url_pe_1)
            print("uploaded_file_url_pe_2: ", uploaded_file_url_pe_2)
            # return HttpResponseRedirect(request.path_info, {
            #     'paired_end': check_files[0],
            #     'single_end': check_files[1],
            #     'uploaded_file_url_1': uploaded_file_url_1,
            #     'uploaded_file_url_2': uploaded_file_url_2,
            # })
            return render(request, "dataanalysis/home.html", {
                'which': "paired-end",
                'project_name': project_name,
                'email': email,
                'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
                'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
                'uploaded_file_url_se': uploaded_file_url_se,
                'remove_file': False,
            })

        elif 'upload-single-end-file' in request.POST:
            print("    * Inside upload-single-end-file")
            myfile1 = request.FILES['s1']
            fs = FileSystemStorage()
            print("Checker path: ", os.path.join(base_dir, "pe"))
            print("Checker path: ", os.path.join(base_dir, "se"))
            if fs.exists(os.path.join(base_dir, "pe")):
                print("Removing files")
                shutil.rmtree(os.path.join(base_dir, "pe"))
            if fs.exists(os.path.join(base_dir, "se")):
                print("Removing files")
                shutil.rmtree(os.path.join(base_dir, "se"))
            ## Found split sample name
            sample_name = os.path.splitext(os.path.splitext(myfile1.name)[0])[0]
            request.session["sample_name"] = sample_name
            print("se_sample_name: ", sample_name)
            request.session["se_or_pe"] = "se"
            print("se_or_pe: ", "se")
            filename1 = fs.save(os.path.join(base_dir, "se", myfile1.name), myfile1)
            uploaded_file_url_se = fs.url(filename1)
            print("uploaded_file_url_se: ", uploaded_file_url_se)
            return render(request, "dataanalysis/home.html", {
                'which': "single-end",
                'project_name': project_name,
                'email': email,
                'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
                'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
                'uploaded_file_url_se': uploaded_file_url_se,
                'remove_file': False,
            })

        elif 'remove-paired-end-file' in request.POST:
            print("    * Inside remove-paired-end-file")
            fs = FileSystemStorage()
            print("Checker path: ", os.path.join(base_dir, "pe"))
            print("Checker path: ", os.path.join(base_dir, "se"))
            if fs.exists(base_dir):
                print("Removing files")
                shutil.rmtree(base_dir)
            return render(request, "dataanalysis/home.html", {
                'which': "single-end",
                'project_name': project_name,
                'email': email,
                'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
                'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
                'uploaded_file_url_se': uploaded_file_url_se,
                'remove_file': True,
            })

        elif 'remove-single-end-file' in request.POST:
            print('    * Inside remove-single-end-file')
            fs = FileSystemStorage()
            print("Checker path: ", os.path.join(base_dir, "pe"))
            print("Checker path: ", os.path.join(base_dir, "se"))
            if fs.exists(base_dir):
                print("Removing files")
                shutil.rmtree(base_dir)
            return render(request, "dataanalysis/home.html", {
                'which': "single-end",
                'project_name': project_name,
                'email': email,
                'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
                'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
                'uploaded_file_url_se': uploaded_file_url_se,
                'remove_file': True,
            })

        elif 'start-analysis' in request.POST:
            print('    * Inside start-analysis')
            prefix_dir = "/Users/chaokuan-hao/Documents/bioinformatics/Virus"
            ### Trimmomatics
            trimmomatic_jar = os.path.join(prefix_dir, "tools/Trimmomatic/trimmomatic-0.38.jar")
            datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                project_name + '_' + email + '_' + analysis_code)
            tool_dir = os.path.join(prefix_dir, "tools")
            fastqc_command = os.path.join(".", tool_dir, "FastQC", "fastqc")
            threads = 8
            phred = "-phred33"
            select_adapter = request.POST.get('trimmomatic_illuminaclip')
            adapter = os.path.join(prefix_dir, "tools/Trimmomatic/adapters", select_adapter)
            adapter_param = ":2:30:10"
            leading = request.POST.get('trimmomatic_leading_quality')
            trailing = request.POST.get('trimmomatic_trailing_quality')
            minlen = request.POST.get('trimmomatic_minlen')
            window_size = request.POST.get('trimmomatic_slidingwindow_size')
            window_quality = request.POST.get('trimmomatic_slidingwindow_quality')

            ### BWA
            bwa_ref = os.path.join(prefix_dir, "host_ref")
            bwa_species = "homo_sapiens.fa"
            host_ref = os.path.join(bwa_ref, bwa_species)

            config_file_path = os.path.join(datadir, 'config.yaml')
            if os.path.exists(os.path.join(datadir, 'pe')):
                se_or_pe = 'pe'
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_pe")
            elif os.path.exists(os.path.join(datadir, 'se')):
                se_or_pe = 'se'
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_se")
            destination_snakemake_file = os.path.join(datadir, 'Snakefile')
            data = dict(
                project_name = project_name,
                datadir = datadir,
                se_or_pe = se_or_pe,
                fastqc = dict(
                    fastqc_command = fastqc_command,
                ),
                trimmomatic = dict(
                    trimmomatic_jar = trimmomatic_jar,
                    threads = threads,
                    phred = phred,
                    adapter = adapter,
                    adapter_param = adapter_param,
                    window_size = window_size,
                    window_quality = window_quality,
                    leading = leading,
                    trailing = trailing,
                    minlen = minlen,
                ),
                bwa = dict(
                    host_ref=host_ref,
                )
            )
            print("Data result: ", data)
            with open(config_file_path, 'w') as ymlfile:
                yaml.dump(data, ymlfile, default_flow_style=False)
            shutil.copyfile(snakemake_file, destination_snakemake_file)
            # subprocess.call(['snakemake'], shell=True, cwd=datadir)
            print(subprocess.call(['pwd']))
            print((reverse('dataanalysis_result_current_status', kwargs={
                  'slug_project': url_parameter})))
            return redirect((reverse('dataanalysis_result_current_status', kwargs={
                'slug_project': url_parameter})))
            # return render(request, "dataanalysis/analysis_result.html")


    return render(request, "dataanalysis/home.html", {
        'which': "normal",
        'project_name': project_name,
        'email': email,
        'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
        'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        'uploaded_file_url_se': uploaded_file_url_se,
        'remove_file': False,
    })


def show_result_overview(request, slug_project):
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
    if 'start_time' in request.session:
        start_time = request.session['start_time']
        print("start_time: ", start_time)
        request.session["start_time"] = start_time
    if 'end_time' in request.session:
        end_time = request.session['end_time']
        print("end_time: ", end_time)
        request.session["end_time"] = end_time
        
    return render(request, "dataanalysis/analysis_result_overview.html", {
        "project_name": project_name,
        "analysis_code": analysis_code,
        "email": email,
    })

    
def show_result(request, slug_project):
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
    url_parameter = project_name + '_' + email.split("@")[0]


    return render(request, "dataanalysis/analysis_result.html", {
        'project_name': project_name,
        'email': email,
        'url_parameter': url_parameter,
    })


def current_status(request, slug_project):
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

    if 'start_time' in request.session:
        start_time = request.session['start_time']
        print("start_time: ", start_time)
        request.session["start_time"] = start_time
    if 'end_time' in request.session:
        end_time = request.session['end_time']
        print("end_time: ", end_time)
        request.session["end_time"] = end_time

    url_parameter = project_name + '_' + email.split("@")[0]

    if ('view_counter_%s' % url_parameter) in request.session:
        view_counter = request.session['view_counter_%s' % url_parameter]
        view_counter = view_counter + 1
        print("&&&&&&&&&view_counter: ", view_counter)
        request.session['view_counter_%s' % url_parameter] = view_counter
    else:
        view_counter = 1
        print("&&&&&&&&&view_counter: ", view_counter)
        request.session['view_counter_%s' % url_parameter] = view_counter
    if request.method == 'POST':
        if 'go-to-overview-button' in request.POST:
            print("clicked button")
            return redirect((reverse('dataanalysis_result_overview', kwargs={
                'slug_project': url_parameter})))

    datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                           project_name + '_' + email + '_' + analysis_code)
    if os.path.exists(os.path.join(datadir, 'pe')):
        se_or_pe = "pe"
    elif os.path.exists(os.path.join(datadir, 'se')):
        se_or_pe = "se"
    files = os.listdir(os.path.join(datadir, se_or_pe))
    sample_name = os.path.splitext(os.path.splitext(
        os.path.splitext(files[0])[0])[0])[0]
    print("&&&&&sample_name: ", sample_name)
    # if 'sample_name' in request.session:
    #     sample_name = request.session['sample_name']
    #     print("sample_name: ", sample_name)
    #     request.session["sample_name"] = sample_name
    # if 'se_or_pe' in request.session:
    #     se_or_pe = request.session['se_or_pe']
    #     print("se_or_pe: ", se_or_pe)
    #     request.session["se_or_pe"] = se_or_pe
    url_parameter = project_name + '_' + email.split("@")[0]
    datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                           project_name + '_' + email + '_' + analysis_code)
    # subprocess.call(['snakemake'], shell=True, cwd=datadir)
    ## If every file is not exist! Run first step!
    # if not(utils_func.check_first_qc(datadir, sample_name, se_or_pe)) and not(utils_func.check_trimming_qc(datadir, sample_name, se_or_pe)) and not(utils_func.check_second_qc(datadir, sample_name, se_or_pe)) is True:
    #     snake_process = subprocess.Popen(
    #         ['snakemake', 'first_fastqc_target'], cwd=datadir)
    #     print(snake_process.returncode)
    #     return render(request, "dataanalysis/analysis_result_overview.html", {
    #         'project_name': project_name,
    #         'email': email,
    #         'url_parameter': url_parameter,
    #     })
    ## If first step is Finished!
    check_first_qc_ans = False
    check_trimming_qc_ans = False
    check_second_qc_ans = False
    check_read_subtraction_bwa_align_ans = False
    view_counter_end = "Not Start Counting"

    if view_counter is 1:
        start_time = str(timezone.now())
        request.session["start_time"] = start_time
        snake_process = subprocess.Popen(['snakemake', 'targets'], cwd=datadir)

    if utils_func.check_first_qc(datadir, sample_name, se_or_pe) is True:
        check_first_qc_ans = True
    if utils_func.check_trimming_qc(datadir, sample_name, se_or_pe) is True:
        check_trimming_qc_ans = True
    if utils_func.check_second_qc(datadir, sample_name, se_or_pe) is True:
        check_second_qc_ans = True
    if utils_func.check_read_subtraction_bwa_align(datadir, sample_name) is True:
        check_read_subtraction_bwa_align_ans = True

    if check_first_qc_ans and check_trimming_qc_ans and check_second_qc_ans and check_read_subtraction_bwa_align_ans:
        if ('view_counter_end_%s' % url_parameter) in request.session:
            view_counter_end = request.session['view_counter_end_%s' % url_parameter]
            view_counter_end = view_counter_end + 1
            print("&&&&&&&&&view_counter: ", view_counter)
            request.session['view_counter_end_%s' % url_parameter] = view_counter_end
        else:
            view_counter_end = 1
            end_time = str(timezone.now())
            request.session["end_time"] = end_time
            print("&&&&&&&&&view_counter_end: ", view_counter_end)
            request.session['view_counter_end_%s' % url_parameter] = view_counter_end
    else:
        end_time = "Not Finish yet"

    print("check_first_qc_ans: ", check_first_qc_ans)
    print("check_trimming_qc_ans: ", check_trimming_qc_ans)
    print("check_second_qc_ans: ", check_second_qc_ans)
    print("check_read_subtraction_bwa_align_ans: ",
          check_read_subtraction_bwa_align_ans)
    return render(request, "dataanalysis/analysis_result_status.html", {
        'project_name': project_name,
        'email': email,
        'url_parameter': url_parameter,
        'check_first_qc_ans': check_first_qc_ans,
        'check_trimming_qc_ans': check_trimming_qc_ans,
        'check_second_qc_ans': check_second_qc_ans,
        'check_read_subtraction_bwa_align_ans': check_read_subtraction_bwa_align_ans,
        'start_time': start_time,
        'end_time': end_time,
        'view_counter_end': view_counter_end,
        'view_counter': view_counter,
    })

def hello_world(request):
    return HttpResponse('Hello World!')


# -*- coding: utf-8 -*-

def upload_progress(request):
    """
    Used by Ajax calls

    Return the upload progress and total length values
    """
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    else:
        progress_id = None

    if progress_id:
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        return HttpResponse(json.dumps(data))


def Check_Uploaded_File_Name(project_name, email, analysis_code):
    uploaded_file_url_pe_1 = None
    uploaded_file_url_pe_2 = None
    uploaded_file_url_se = None
    pe_files = []
    se_files = []
    datadir = os.path.join(settings.MEDIA_ROOT, 'tmp', project_name + '_' + email + '_' + analysis_code)
    upload_dir_pe = os.path.join(datadir, "pe")
    if os.path.exists(upload_dir_pe):
        pe_files = os.listdir(upload_dir_pe)
        print(pe_files)
        for file_check in pe_files:
            print(file_check)
            if ".R1.fastq" in file_check:
                uploaded_file_url_pe_1 = os.path.join(datadir, "pe", file_check)
            if ".R2.fastq" in file_check:
                uploaded_file_url_pe_2 = os.path.join(datadir, "pe", file_check)
        print("uploaded_file_url_pe_1: ", uploaded_file_url_pe_1)
        print("uploaded_file_url_pe_2: ", uploaded_file_url_pe_2)
        # uploaded_file_url_pe_1 = os.path.join(upload_dir_pe, pe_files[0])
        # uploaded_file_url_pe_2 = os.path.join(upload_dir_pe, pe_files[1])
    upload_dir_se = os.path.join(datadir, "se")
    if os.path.exists(upload_dir_se):
        se_files = os.listdir(upload_dir_se)
        uploaded_file_url_se = os.path.join(datadir, "se", se_files[0])

    # files = glob.glob(upload_dir)

    return (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se)

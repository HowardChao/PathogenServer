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

from dataanalysis.models import Document, PairedEnd, SingleEnd
from dataanalysis.forms import DocumentForm, PairedEndForm, SingleEndForm

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

def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dataanalysis_home')
    else:
        form = DocumentForm()
    return render(request, 'dataanalysis/model_form_upload.html', {
        'form': form
    })

def simple_upload(request):
    print("Inside simple_upload()")
    if request.method == 'POST':
        print("Inside POST")
        if 'snakefile-creation' in request.POST:
            prefix_dir = "/Users/chaokuan-hao/Documents/bioinformatics/Virus"
            project_name = "Project62a7db0029ba11e9b31a60f81dacbf14_6bab321a29ba11e9b31a60f81dacbf14"
            trimmomatic_jar = os.path.join(prefix_dir, "tools/Trimmomatic/trimmomatic-0.38.jar")
            datadir = os.path.join(settings.MEDIA_ROOT, 'tmp', project_name)
            tool_dir = os.path.join(prefix_dir, "tools")
            fastqc_command = os.path.join(".", tool_dir, "FastQC", "fastqc")
            threads = 8
            phred = "-phred33"
            trimlog = "trimmomatic_log"
            adapter = os.path.join(prefix_dir, "tools/Trimmomatic/adapters/TruSeq3-PE.fa")
            adapter_param = ":2:30:10"
            leading = 3
            trailing = 3
            minlen = 36
            window_size = 4
            window_quality = 20
            config_file_path = os.path.join(settings.MEDIA_ROOT, 'tmp', project_name, 'config.yaml')
            if os.path.exists(os.path.join(datadir, 'pe')):
                se_or_pe = 'pe'
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_pe")
            elif os.path.exists(os.path.join(datadir, 'se')):
                se_or_pe = 'se'
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_se")
            destination_snakemake_file = os.path.join(settings.MEDIA_ROOT, 'tmp', project_name, 'Snakefile')
            data = dict(
                project_name = project_name,
                Fuck = "Fucl",
                datadir = datadir,
                tool_dir = tool_dir,
                se_or_pe = se_or_pe,
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
                fastqc = dict(
                    fastqc_command = fastqc_command,
                ),
            )
            with open(config_file_path, 'w') as ymlfile:
                yaml.dump(data, ymlfile, default_flow_style=False)
            shutil.copyfile(snakemake_file, destination_snakemake_file)
            subprocess.call(['snakemake'], shell=True, cwd=datadir)
            print(subprocess.call(['pwd']))
            return render(request, 'dataanalysis/simple_upload.html')
    return render(request, 'dataanalysis/simple_upload.html')



def paired_end_upload(request, slug_project):
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
                )
            )
            print("Data result: ", data)
            with open(config_file_path, 'w') as ymlfile:
                yaml.dump(data, ymlfile, default_flow_style=False)
            shutil.copyfile(snakemake_file, destination_snakemake_file)
            subprocess.call(['snakemake'], shell=True, cwd=datadir)
            print(subprocess.call(['pwd']))
            # return render(reverse('dataanalysis_result', kwargs={
            #         'slug_project': url_parameter}))
            print((reverse('dataanalysis_result', kwargs={
                  'slug_project': url_parameter})))
            return redirect((reverse('dataanalysis_result', kwargs={
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
    url_parameter = project_name + '_' + email.split("@")[0]

    return render(request, "dataanalysis/analysis_result_overview.html", {
        'project_name': project_name,
        'email': email,
        'url_parameter': url_parameter,
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

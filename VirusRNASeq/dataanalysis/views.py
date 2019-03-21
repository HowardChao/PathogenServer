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

# Creating GET and POST functions!! When we access page, we are going to
# show the user a list of uploaded files

def post(self, request):
    form = DataForm(self.request.POST, self.request.FILES)
    if form.is_valid():
        data = form.save()
        data = {'is_valid': True, 'name': data.file.name, 'url': data.file.url}
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


def data_analysis_home(request):

    if request.method == 'POST' and request.FILES['myfile1']:
        project_name = "None"
        analysis_code = "None"
        myfile = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        filename2 = fs.save(myfile2.name, myfile2)
        uploaded_file_url = fs.url(filename)
        uploaded_file_url2 = fs.url(filename2)
        return render(request, 'dataanalysis/analysis_home_denovo.html', {
            'uploaded_file_url': uploaded_file_url,
            'uploaded_file_url2': uploaded_file_url2,
        })
    return render(request, 'dataanalysis/analysis_home_denovo.html')
    # documents = Document.objects.all()
    # return render(request, 'dataanalysis/analysis_home_denovo.html', { 'documents': documents })

class BasicUploadView(DetailView):
    # slug_field = 'my_cool_field'
    template_name = 'dataanalysis/data_upload.html'
    samples_txt_file_name = None
    samples_list_key = {}
    def get(self, request, slug_project):
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
        # The base directory of the created project.
        multi_or_one = "multiple_samples"
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        # The url for the slug_project
        url_parameter = project_name + '_' + email.split("@")[0]
        # Start checking files !!!
        (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
        uploaded_file = check_upload_sample_name(project_name, email, analysis_code)
        data_list = []
        for key in uploaded_file:
            for file in uploaded_file[key]:
                data_list.append(key + file)
        (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se) = Check_Uploaded_File_Name(
            project_name, email, analysis_code)
        return render(self.request, "dataanalysis/file_upload.html", {
            'project_name': project_name,
            'analysis_code': analysis_code,
            'email': email,
            'assembly_type_input': assembly_type_input,
            'datas': data_list,
            'samples_txt_file_name': samples_txt_file_name,
            'samples_list_key': samples_list_key,
            'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
            'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        })

    def post(self, request, slug_project):
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
        url_parameter = project_name + '_' + email.split("@")[0]
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
        if assembly_type_input == "de_novo_assembly":
            template_html = "dataanalysis/analysis_home_denovo.html"
        elif assembly_type_input == "reference_based_assembly":
            template_html = "dataanalysis/analysis_home_reference_based.html"
        multi_or_one = "multiple_samples"

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
            (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
            samples_list_key = samples_list_key
            uploaded_file = check_upload_sample_name(project_name, email, analysis_code)
            data_list = []
            for key in uploaded_file:
                for file in uploaded_file[key]:
                    data_list.append(key + file)
            return render(request, "dataanalysis/file_upload.html", {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'datas': data_list,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
            })
        elif 'remove-samples-file' in request.POST:
            print("remove-samples-file!!!")
            samples_txt_file_name = None
            fs = FileSystemStorage()
            if fs.exists(base_dir):
                shutil.rmtree(base_dir)
            destination_QC_html_dir = os.path.join(os.path.dirname(__file__), 'templates', 'dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code)
            if os.path.exists(destination_QC_html_dir):
                shutil.rmtree(destination_QC_html_dir)
            # Start checking files
            (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
            samples_list_key = samples_list_key
            uploaded_file = check_upload_sample_name(project_name, email, analysis_code)
            data_list = []
            for key in uploaded_file:
                for file in uploaded_file[key]:
                    data_list.append(key + file)
            return render(request, "dataanalysis/file_upload.html", {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'datas': data_list,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
            })
        elif 'multi_samples_workflow_setup_button' in request.POST:
            (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
            samples_list_key = samples_list_key
            uploaded_file = check_upload_sample_name(project_name, email, analysis_code)
            data_list = []
            for key in uploaded_file:
                for file in uploaded_file[key]:
                    data_list.append(key + file)
            print("$$$$data_list: ")
            return render(request, template_html, {
                'project_name': project_name,
                'analysis_code': analysis_code,
                'email': email,
                'assembly_type_input': assembly_type_input,
                'datas': data_list,
                'samples_txt_file_name': samples_txt_file_name,
                'samples_list_key': samples_list_key,
            })

        # ######################
        # ## One sample section
        # elif 'upload-paired-end-file' in request.POST:
        #     print("upload-paired-end-fileupload-paired-end-file")
        #     uploaded_file_url_pe_1 = None
        #     uploaded_file_url_pe_2 = None
        #     uploaded_file_url_se = None
        #     base_dir = os.path.join(settings.MEDIA_ROOT,
        #                             'tmp', project_name + '_' + email + '_' + analysis_code)
        #     myfile1 = request.FILES['r1']
        #     myfile2 = request.FILES['r2']
        #     fs = FileSystemStorage()
        #     # Removing files
        #     if fs.exists(os.path.join(base_dir, 'Uploaded_files', 'one')):
        #         shutil.rmtree(os.path.join(base_dir, "Uploaded_files", "one"))
        #     ## Found split sample name
        #     sample_name = os.path.splitext(os.path.splitext(
        #         os.path.splitext(myfile1.name)[0])[0])[0]
        #     request.session["sample_name"] = sample_name
        #     filename1 = fs.save(os.path.join(base_dir, 'Uploaded_files', 'one', sample_name, myfile1.name), myfile1)
        #     filename2 = fs.save(os.path.join(base_dir, 'Uploaded_files', 'one', sample_name, myfile2.name), myfile2)
        #     uploaded_file_url_pe_1 = fs.url(filename1)
        #     uploaded_file_url_pe_2 = fs.url(filename2)
        #     (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se) = Check_Uploaded_File_Name(
        #         project_name, email, analysis_code)
        #     return render(request, "dataanalysis/file_upload.html", {
        #         'project_name': project_name,
        #         'analysis_code': analysis_code,
        #         'email': email,
        #         'assembly_type_input': assembly_type_input,
        #         'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
        #         'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        #         'uploaded_file_url_se': uploaded_file_url_se,
        #     })
        #
        # elif 'remove-paired-end-file' in request.POST:
        #     fs = FileSystemStorage()
        #     one_smaple_base_dir = os.path.join(base_dir, "Uploaded_files", "one")
        #     if fs.exists(one_smaple_base_dir):
        #         shutil.rmtree(base_dir)
        #     destination_QC_html_dir = os.path.join(os.path.dirname(__file__), 'templates', 'dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code)
        #     if os.path.exists(destination_QC_html_dir):
        #         shutil.rmtree(destination_QC_html_dir)
        #     (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se) = Check_Uploaded_File_Name(
        #         project_name, email, analysis_code)
        #     return render(request, "dataanalysis/file_upload.html", {
        #         'which': "single-end",
        #         'project_name': project_name,
        #         'email': email,
        #         'assembly_type_input': assembly_type_input,
        #         'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
        #         'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        #         'uploaded_file_url_se': uploaded_file_url_se,
        #     })
        #
        # elif 'one_sample_workflow_setup_button' in request.POST:
        #     request.session["multi_or_one"] = "one_sample"
        #     uploaded_file = check_upload_sample_name(project_name, email, analysis_code)
        #     data_list = []
        #     for key in uploaded_file:
        #         for file in uploaded_file[key]:
        #             data_list.append(key + file)
        #     return render(request, template_html, {
        #         'project_name': project_name,
        #         'analysis_code': analysis_code,
        #         'email': email,
        #         'assembly_type_input': assembly_type_input,
        #         'datas': data_list,
        #         'samples_txt_file_name': samples_txt_file_name,
        #         'samples_list_key': samples_list_key,
        #     })

        # if 'sample-each-upload-many' in request.POST:
        # elif 'sample-each-upload-many' in request.POST:
        myfile = request.FILES['file_choose']
        fs = FileSystemStorage()
        sample_name = os.path.splitext(os.path.splitext(os.path.splitext(myfile.name)[0])[0])[0]
        print("&&&&& sample_name: ", sample_name)
        # Removing files
        if not fs.exists(os.path.join(base_dir, 'Uploaded_files')):
            os.mkdir((os.path.join(base_dir, 'Uploaded_files')))
            if not fs.exists(os.path.join(base_dir, 'Uploaded_files', "multi")):
                os.mkdir((os.path.join(base_dir, 'Uploaded_files', "multi")))
                if not fs.exists(os.path.join(base_dir, 'Uploaded_files', "multi", sample_name)):
                    os.mkdir((os.path.join(base_dir, 'Uploaded_files', "multi", sample_name)))
                # Found split sample name
        sample_name = os.path.splitext(os.path.splitext(os.path.splitext(myfile.name)[0])[0])[0]
        filename = fs.save(os.path.join(base_dir, "Uploaded_files", "multi", sample_name, myfile.name), myfile)
        uploaded_file_url = fs.url(filename)
        # Start checking files
        (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
        samples_list_key = samples_list_key
        uploaded_file = check_upload_sample_name(project_name, email, analysis_code)
        data_list = []
        for key in uploaded_file:
            for file in uploaded_file[key]:
                data_list.append(key + file)
        data = {
            'project_name': project_name,
            'analysis_code': analysis_code,
            'email': email,
            'assembly_type_input': assembly_type_input,
            'is_valid': True,
            'name': myfile.name,
            'datas': data_list,
            'samples_txt_file_name': samples_txt_file_name,
            'samples_list_key': samples_list_key}
        return JsonResponse(data)






def check_upload_sample_name(project_name, email, analysis_code):
    uploaded_file = {}
    datadir = os.path.join(settings.MEDIA_ROOT, 'tmp', project_name + '_' + email + '_' + analysis_code)
    upload_dir = os.path.join(datadir, "Uploaded_files")
    if os.path.exists(upload_dir):
        samples_dir = os.listdir(upload_dir)
        for sample in samples_dir:
            fastqs_in_sample = []
            for fastq in os.listdir(os.path.join(upload_dir, sample)):
                print("fastq", fastq)
                if ".R1.fastq.gz" in fastq:
                    fastq_pe_1 = os.path.join(datadir, "Uploaded_files", sample, fastq)
                    fastqs_in_sample.append(fastq_pe_1)
                if ".R2.fastq.gz" in fastq:
                    fastq_pe_2 = os.path.join(datadir, "Uploaded_files", sample, fastq)
                    fastqs_in_sample.append(fastq_pe_2)
            uploaded_file[sample] = fastqs_in_sample
    print("uploaded_file$$$$: ", uploaded_file)
    return uploaded_file






def data_upload(request, slug_project):
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
    url_parameter = project_name + '_' + email.split("@")[0]
    return render(request, "dataanalysis/data_upload.html", {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })



def whole_dataanalysis(request, slug_project):
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se) = Check_Uploaded_File_Name(
        project_name, email, analysis_code)
    url_parameter = project_name + '_' + email.split("@")[0]
    if assembly_type_input == "de_novo_assembly":
        template_html = "dataanalysis/analysis_home_denovo.html"
    elif assembly_type_input == "reference_based_assembly":
        template_html = "dataanalysis/analysis_home_reference_based.html"
    if request.method == 'POST' :
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
        # if 'upload-paired-end-file' in request.POST:
        #     myfile1 = request.FILES['r1']
        #     myfile2 = request.FILES['r2']
        #     fs = FileSystemStorage()
        #     # Removing files
        #     if fs.exists(os.path.join(base_dir, 'pe')):
        #         shutil.rmtree(os.path.join(base_dir, "pe"))
        #     if fs.exists(os.path.join(base_dir, "se")):
        #         shutil.rmtree(os.path.join(base_dir, "se"))
        #     ## Found split sample name
        #     sample_name = os.path.splitext(os.path.splitext(
        #         os.path.splitext(myfile1.name)[0])[0])[0]
        #     request.session["sample_name"] = sample_name
        #     request.session["se_or_pe"] = "pe"
        #     filename1 = fs.save(os.path.join(base_dir, "pe", myfile1.name), myfile1)
        #     filename2 = fs.save(os.path.join(base_dir, "pe", myfile2.name), myfile2)
        #     uploaded_file_url_pe_1 = fs.url(filename1)
        #     uploaded_file_url_pe_2 = fs.url(filename2)
        #     return render(request, template_html, {
        #         'which': "paired-end",
        #         'project_name': project_name,
        #         'email': email,
        #         'assembly_type_input': assembly_type_input,
        #         'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
        #         'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        #         'uploaded_file_url_se': uploaded_file_url_se,
        #         'remove_file': False,
        #     })
        # elif 'remove-paired-end-file' in request.POST:
        #     fs = FileSystemStorage()
        #     if fs.exists(base_dir):
        #         shutil.rmtree(base_dir)
        #     destination_QC_html_dir = os.path.join(os.path.dirname(__file__), 'templates', 'dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code)
        #     if os.path.exists(destination_QC_html_dir):
        #         shutil.rmtree(destination_QC_html_dir)
        #     return render(request, template_html, {
        #         'which': "single-end",
        #         'project_name': project_name,
        #         'email': email,
        #         'assembly_type_input': assembly_type_input,
        #         'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
        #         'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        #         'uploaded_file_url_se': uploaded_file_url_se,
        #         'remove_file': True,
        #     })
        if 'start-analysis' in request.POST:
            upload_files_dir = os.path.join(base_dir, "Uploaded_files")
            prefix_dir = "/ssd/Howard/Virus/"
            tool_dir = os.path.join(prefix_dir, "tools")
            host_ref_dir = os.path.join(prefix_dir, "host_ref")
            pathogen_dir = os.path.join(prefix_dir, "pathogen")
            (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
            datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                project_name + '_' + email + '_' + analysis_code)
            ### Trimmomatics
            trimmomatic_jar = os.path.join(prefix_dir, "tools/Trimmomatic/trimmomatic-0.38.jar")
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
            species_dir = "homo_sapiens"
            bwa_species = "homo_sapiens.fa"
            bwa_ref = os.path.join(prefix_dir, "host_ref", species_dir)
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
            with open(config_file_path, 'w') as ymlfile:
                yaml.dump(data, ymlfile, default_flow_style=False)
            shutil.copyfile(snakemake_file, destination_snakemake_file)
            if (not os.path.exists(os.path.join(datadir, 'script'))):
                os.mkdir((os.path.join(datadir, 'script')))
            for name in ['start', 'end']:
                get_time_script = os.path.join(
                    prefix_dir, "VirusRNASeq/VirusRNASeq/script/get_" + name + "_time.py")
                destination_get_time_script = os.path.join(
                    datadir, 'script/get_' + name + '_time.py')
                shutil.copyfile(get_time_script, destination_get_time_script)
            # subprocess.call(['snakemake'], shell=True, cwd=datadir)
            return redirect((reverse('dataanalysis_result_current_status', kwargs={
                'slug_project': url_parameter})))
    return render(request, template_html, {
        'which': "normal",
        'project_name': project_name,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
        'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        'uploaded_file_url_se': uploaded_file_url_se,
        'remove_file': False,
    })


def whole_dataanalysis_reference_based(request, slug_project):
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
    url_parameter = project_name + '_' + email.split("@")[0]
    template_html = "dataanalysis/analysis_home_reference_based.html"
    if request.method == 'POST' :
        base_dir = os.path.join(settings.MEDIA_ROOT,
                                'tmp', project_name + '_' + email + '_' + analysis_code)
    upload_files_dir = os.path.join(base_dir, "Uploaded_files")
    prefix_dir = "/ssd/Howard/Virus/"
    tools_dir = os.path.join(prefix_dir, "tools")
    host_ref_dir = os.path.join(prefix_dir, "host_ref")
    pathogen_dir = os.path.join(prefix_dir, "pathogen")
    (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
    print("samples_txt_file_name: ", samples_txt_file_name)


        if 'start-analysis-de-novo' in request.POST:

            ### Tools variable
            ### Trimmomatics
            trimmomatic_jar = os.path.join(prefix_dir, "tools/Trimmomatic/trimmomatic-0.38.jar")
            datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                project_name + '_' + email + '_' + analysis_code)
            tool_dir = os.path.join(prefix_dir, "tools")
            fastqc_command = os.path.join(".", tool_dir, "FastQC", "fastqc")
            trimmomatic_threads = 8
            trimmomatic_phred = "-phred33"
            trimmomatic_select_adapter = request.POST.get('trimmomatic_illuminaclip')
            trimmomatic_adapter = os.path.join(prefix_dir, "tools/Trimmomatic/adapters", select_adapter)
            trimmomatic_adapter_param = ":2:30:10"
            trimmomatic_leading = request.POST.get('trimmomatic_leading_quality')
            trimmomatic_trailing = request.POST.get('trimmomatic_trailing_quality')
            trimmomatic_minlen = request.POST.get('trimmomatic_minlen')
            trimmomatic_window_size = request.POST.get('trimmomatic_slidingwindow_size')
            trimmomatic_window_quality = request.POST.get('trimmomatic_slidingwindow_quality')

            ### BWA
            species_dir = "homo_sapiens"
            bwa_species = "homo_sapiens.fa"
            bwa_ref = os.path.join(host_ref_dir, species_dir)
            bwa_host_ref = os.path.join(bwa_ref, bwa_species)

            config_file_path = os.path.join(datadir, 'config.yaml')
            if os.path.exists(os.path.join(datadir)):
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_de_novo")
            elif os.path.exists(os.path.join(datadir)):
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_reference_based")
            destination_snakemake_file = os.path.join(datadir, 'Snakefile')
            data = dict(
                project_name = project_name,
                datadir = datadir,
                fastqc = dict(
                    fastqc_command = fastqc_command,
                ),
                trimmomatic = dict(
                    trimmomatic_jar = trimmomatic_jar,
                    threads = trimmomatic_threads,
                    phred = trimmomatic_phred,
                    adapter = trimmomatic_adapter,
                    adapter_param = trimmomatic_adapter_param,
                    window_size = trimmomatic_window_size,
                    window_quality = trimmomatic_window_quality,
                    leading = trimmomatic_leading,
                    trailing = trimmomatic_trailing,
                    minlen = trimmomatic_minlen,
                ),
                bwa = dict(
                    host_ref=bwa_host_ref,
                )
            )
            with open(config_file_path, 'w') as ymlfile:
                yaml.dump(data, ymlfile, default_flow_style=False)
            shutil.copyfile(snakemake_file, destination_snakemake_file)
            if (not os.path.exists(os.path.join(datadir, 'script'))):
                os.mkdir((os.path.join(datadir, 'script')))
            for name in ['start', 'end']:
                get_time_script = os.path.join(
                    prefix_dir, "VirusRNASeq/VirusRNASeq/script/get_" + name + "_time.py")
                destination_get_time_script = os.path.join(
                    datadir, 'script/get_' + name + '_time.py')
                shutil.copyfile(get_time_script, destination_get_time_script)
            # subprocess.call(['snakemake'], shell=True, cwd=datadir)
            return redirect((reverse('dataanalysis_result_current_status', kwargs={
                'slug_project': url_parameter})))






        elif 'start-analysis-reference-based' in request.POST:
            upload_files_dir = os.path.join(base_dir, "Uploaded_files")
            prefix_dir = "/ssd/Howard/Virus/"
            tools_dir = os.path.join(prefix_dir, "tools")
            host_ref_dir = os.path.join(prefix_dir, "host_ref")
            pathogen_dir = os.path.join(prefix_dir, "pathogen")
            (samples_txt_file_name, samples_list_key) = utils_func.check_samples_txt_file(base_dir)
            print("samples_txt_file_name: ", samples_txt_file_name)
            ### Tools variable
            ### Trimmomatics
            trimmomatic_jar = os.path.join(prefix_dir, "tools/Trimmomatic/trimmomatic-0.38.jar")
            datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                project_name + '_' + email + '_' + analysis_code)
            tool_dir = os.path.join(prefix_dir, "tools")
            fastqc_command = os.path.join(".", tool_dir, "FastQC", "fastqc")
            trimmomatic_threads = 8
            trimmomatic_phred = "-phred33"
            trimmomatic_select_adapter = request.POST.get('trimmomatic_illuminaclip')
            trimmomatic_adapter = os.path.join(prefix_dir, "tools/Trimmomatic/adapters", select_adapter)
            trimmomatic_adapter_param = ":2:30:10"
            trimmomatic_leading = request.POST.get('trimmomatic_leading_quality')
            trimmomatic_trailing = request.POST.get('trimmomatic_trailing_quality')
            trimmomatic_minlen = request.POST.get('trimmomatic_minlen')
            trimmomatic_window_size = request.POST.get('trimmomatic_slidingwindow_size')
            trimmomatic_window_quality = request.POST.get('trimmomatic_slidingwindow_quality')

            ### BWA
            species_dir = "homo_sapiens"
            bwa_species = "homo_sapiens.fa"
            bwa_ref = os.path.join(host_ref_dir, species_dir)
            bwa_host_ref = os.path.join(bwa_ref, bwa_species)

            config_file_path = os.path.join(datadir, 'config.yaml')
            if os.path.exists(os.path.join(datadir)):
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_de_novo")
            elif os.path.exists(os.path.join(datadir)):
                snakemake_file = os.path.join(prefix_dir, "VirusRNASeq/VirusRNASeq/Snakefile_reference_based")
            destination_snakemake_file = os.path.join(datadir, 'Snakefile')
            data = dict(
                project_name = project_name,
                datadir = datadir,
                fastqc = dict(
                    fastqc_command = fastqc_command,
                ),
                trimmomatic = dict(
                    trimmomatic_jar = trimmomatic_jar,
                    threads = trimmomatic_threads,
                    phred = trimmomatic_phred,
                    adapter = trimmomatic_adapter,
                    adapter_param = trimmomatic_adapter_param,
                    window_size = trimmomatic_window_size,
                    window_quality = trimmomatic_window_quality,
                    leading = trimmomatic_leading,
                    trailing = trimmomatic_trailing,
                    minlen = trimmomatic_minlen,
                ),
                bwa = dict(
                    host_ref=bwa_host_ref,
                )
            )
            with open(config_file_path, 'w') as ymlfile:
                yaml.dump(data, ymlfile, default_flow_style=False)
            shutil.copyfile(snakemake_file, destination_snakemake_file)
            if (not os.path.exists(os.path.join(datadir, 'script'))):
                os.mkdir((os.path.join(datadir, 'script')))
            for name in ['start', 'end']:
                get_time_script = os.path.join(
                    prefix_dir, "VirusRNASeq/VirusRNASeq/script/get_" + name + "_time.py")
                destination_get_time_script = os.path.join(
                    datadir, 'script/get_' + name + '_time.py')
                shutil.copyfile(get_time_script, destination_get_time_script)
            # subprocess.call(['snakemake'], shell=True, cwd=datadir)
            return redirect((reverse('dataanalysis_result_current_status', kwargs={
                'slug_project': url_parameter})))
    return render(request, template_html, {
        'which': "normal",
        'project_name': project_name,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
        'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        'uploaded_file_url_se': uploaded_file_url_se,
        'remove_file': False,
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
    if 'se_or_pe' in request.session:
        se_or_pe = request.session['se_or_pe']
        print("se_or_pe: ", se_or_pe)
        request.session["se_or_pe"] = se_or_pe
    # Get submission time
    submission_time_file = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                        project_name + '_' + email + '_' + analysis_code, 'submision_time.txt')
    submission_time_strip = 'no submission time'
    if os.path.exists(submission_time_file):
        f_submission = open(submission_time_file, "r")
        submission_time_strip = f_submission.read()
    # Get start time
    start_time_file = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                   project_name + '_' + email + '_' + analysis_code, 'start_time.txt')
    start_time_strip = 'no start time'
    if os.path.exists(start_time_file):
        f_start = open(start_time_file, "r")
        start_time_strip = f_start.read()
    # Get end time
    end_time_file = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                   project_name + '_' + email + '_' + analysis_code, 'end_time.txt')
    end_time_strip = 'no end time'
    if os.path.exists(end_time_file):
        f_end = open(end_time_file, "r")
        end_time_strip = f_end.read()
    qc_datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                              project_name + '_' + email + '_' + analysis_code, 'QC')

    url_parameter = project_name + '_' + email.split("@")[0]
    if se_or_pe == 'pe':
        sample_name = utils_func.get_pe_sample_name(se_or_pe, project_name, email, analysis_code)
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

        destination_QC_html_dir = os.path.join(os.path.dirname(__file__), 'templates', 'dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, 'QC')
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
    elif se_or_pe == 'se':
        pass
        qc_datadir_pre = os.path.join(qc_datadir, 'pre', )
        qc_datadir_post = os.path.join(qc_datadir, 'post', )

    trimmomatic_command_log = os.path.join(settings.MEDIA_ROOT, 'tmp', project_name + '_' + email + '_' + analysis_code, 'logs', 'trimmomatic_'+se_or_pe, sample_name+'.command.log')
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    url_parameter = project_name + '_' + email.split("@")[0]
    return render(request, "dataanalysis/analysis_result.html", {
        'project_name': project_name,
        'email': email,
        'assembly_type_input':assembly_type_input,
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    submission_time_file = os.path.join(settings.MEDIA_ROOT, 'tmp',
                                        project_name + '_' + email + '_' + analysis_code, 'submision_time.txt')
    submission_time_strip = 'no submission time'
    if os.path.exists(submission_time_file):
        f_submission = open(submission_time_file, "r")
        submission_time_strip = f_submission.read()
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

    datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                           project_name + '_' + email + '_' + analysis_code)

    if os.path.exists(os.path.join(datadir, 'pe')):
        se_or_pe = "pe"
    elif os.path.exists(os.path.join(datadir, 'se')):
        se_or_pe = "se"
    request.session["se_or_pe"] = se_or_pe
    files = os.listdir(os.path.join(datadir, se_or_pe))
    sample_name = os.path.splitext(os.path.splitext(
        os.path.splitext(files[0])[0])[0])[0]
    url_parameter = project_name + '_' + email.split("@")[0]
    datadir = os.path.join(settings.MEDIA_ROOT, 'tmp',
                           project_name + '_' + email + '_' + analysis_code)
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
    if utils_func.check_submission_time_file(datadir, sample_name, se_or_pe) is True:
        check_submission_time_ans = True
    if utils_func.check_first_qc(datadir, sample_name, se_or_pe) is True:
        check_first_qc_ans = True
    if utils_func.check_trimming_qc(datadir, sample_name, se_or_pe) is True:
        check_trimming_qc_ans = True
    if utils_func.check_second_qc(datadir, sample_name, se_or_pe) is True:
        check_second_qc_ans = True
    if utils_func.check_read_subtraction_bwa_align(datadir, sample_name) is True:
        check_read_subtraction_bwa_align_ans = True
    if utils_func.check_extract_non_host_reads_1(datadir, sample_name) is True:
        check_extract_non_host_reads_1_ans = True
    if utils_func.check_extract_non_host_reads_2(datadir, sample_name) is True:
        check_extract_non_host_reads_2_ans = True
    if utils_func.check_extract_non_host_reads_3(datadir, sample_name) is True:
        check_extract_non_host_reads_3_ans = True
    if utils_func.check_extract_non_host_reads_4(datadir, sample_name) is True:
        check_extract_non_host_reads_4_ans = True
    if utils_func.check_end_time_file(datadir, sample_name, se_or_pe) is True:
        check_end_time_ans = True
    whole_file_check = check_first_qc_ans and check_trimming_qc_ans and check_second_qc_ans and check_read_subtraction_bwa_align_ans
    if ((view_counter is 1) or (check_submission_time_ans is False and check_first_qc_ans is False and check_trimming_qc_ans is False and check_second_qc_ans is False and check_read_subtraction_bwa_align_ans is False and check_end_time_ans is False) or submission_time_strip == 'no submission time'):
        # This is the first time to run (with the submission time stamp)
        submission_time = timezone.now()
        submission_time_strip = submission_time.strftime("%B %d, %Y, %I:%M:%S %p")
        f_submission = open(submission_time_file, 'w')
        f_submission.writelines(submission_time_strip)
        f_submission.close()
        # request.session["submission_time"] = submission_time_strip
        subprocess.Popen(['snakemake', 'targets'], cwd=datadir)
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
        for file_check in pe_files:
            if ".R1.fastq" in file_check:
                uploaded_file_url_pe_1 = os.path.join(datadir, "pe", file_check)
            if ".R2.fastq" in file_check:
                uploaded_file_url_pe_2 = os.path.join(datadir, "pe", file_check)
        # uploaded_file_url_pe_1 = os.path.join(upload_dir_pe, pe_files[0])
        # uploaded_file_url_pe_2 = os.path.join(upload_dir_pe, pe_files[1])
    upload_dir_se = os.path.join(datadir, "se")
    if os.path.exists(upload_dir_se):
        se_files = os.listdir(upload_dir_se)
        uploaded_file_url_se = os.path.join(datadir, "se", se_files[0])

    # files = glob.glob(upload_dir)

    return (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se)

def pre_qc_html_view_multiqc(request, slug_project):
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    url_parameter = project_name + '_' + email.split("@")[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, 'QC', 'pre', 'Tochigi-7_S6_L001_multiqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def pre_qc_html_view_r1(request, slug_project):
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    url_parameter = project_name + '_' + email.split("@")[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, 'QC', 'pre', 'Tochigi-7_S6_L001.R1_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def pre_qc_html_view_r2(request, slug_project):
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    url_parameter = project_name + '_' + email.split("@")[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, 'QC', 'pre', 'Tochigi-7_S6_L001.R2_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_multiqc(request, slug_project):
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    url_parameter = project_name + '_' + email.split("@")[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, 'QC', 'post', 'Tochigi-7_S6_L001_multiqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_r1(request, slug_project):
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    url_parameter = project_name + '_' + email.split("@")[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, 'QC', 'post', 'Tochigi-7_S6_L001_r1_paired_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

def post_qc_html_view_r2(request, slug_project):
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
    if 'assembly_type_input' in request.session:
        assembly_type_input = request.session['assembly_type_input']
        print("assembly_type_input: ", assembly_type_input)
        request.session["assembly_type_input"] = assembly_type_input
    url_parameter = project_name + '_' + email.split("@")[0]
    html_file = os.path.join('dataanalysis', 'tmp', project_name + '_' + email + '_' + analysis_code, 'QC', 'post', 'Tochigi-7_S6_L001_r2_paired_fastqc.html')
    return render(request, html_file, {
        'project_name': project_name,
        'analysis_code': analysis_code,
        'email': email,
        'assembly_type_input': assembly_type_input,
        'url_parameter': url_parameter,
    })

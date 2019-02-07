from django.core.cache import cache
from django.http import HttpResponse
import json
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.conf import settings
import glob
import os
import shutil
import re

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

def simple_upload(request):
    print("Inside simple_upload()")
    if request.method == 'POST' and request.FILES['myfile']:
        project_name = "None"
        analysis_code = "None"
        if 'project_name' in request.session:
            project_name = request.session['project_name']
        if 'analysis_code' is request.session:
            analysis_code = request.session['analysis_code']
        print("project_name: ", project_name)
        print("analysis_code: ", analysis_code)
        # upload_dir = os.path.join(TMP_DIR, tmp_project_id, "reads")
        # print("upload_dir id: ", upload_dir)
        # if not os.path.exists(upload_dir):
        #     os.makedirs(upload_dir)
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'dataanalysis/simple_upload.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'dataanalysis/simple_upload.html')

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

def paired_end_upload(request):
    print("Inside data_analysis_home !!!")

    ## Check if file exist !!
    # os.listdir(settings)
    uploaded_file_url_pe_1 = None
    uploaded_file_url_pe_2 = None
    uploaded_file_url_se = None
    if 'project_name' in request.session:
        project_name = request.session['project_name']
        print("project_name: ", project_name)
    if 'analysis_code' is request.session:
        analysis_code = request.session['analysis_code']
        print("analysis_code: ", analysis_code)
    (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se) = Check_Uploaded_File_Name(
        project_name)
    if request.method == 'POST' :
        print("paired_or_single: ", request.POST['paired_or_single'])
        if request.POST['paired_or_single'] == "paired":
            myfile1 = request.FILES['r1']
            myfile2 = request.FILES['r2']
            fs = FileSystemStorage()
            print("Checker path: ", os.path.join(settings.MEDIA_ROOT, project_name, "pe"))
            print("Checker path: ", os.path.join(
                settings.MEDIA_ROOT, project_name, "se"))
            if fs.exists(os.path.join(settings.MEDIA_ROOT, project_name, "pe")):
                print("Removing files")
                shutil.rmtree(os.path.join(
                    settings.MEDIA_ROOT, project_name, "pe"))
            if fs.exists(os.path.join(settings.MEDIA_ROOT, project_name, "se")):
                print("Removing files")
                shutil.rmtree(os.path.join(
                    settings.MEDIA_ROOT, project_name, "se"))
            filename1 = fs.save(os.path.join(project_name, "pe", myfile1.name), myfile1)
            filename2 = fs.save(os.path.join(project_name, "pe", myfile2.name), myfile2)
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
                'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
                'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
                'uploaded_file_url_se': uploaded_file_url_se,
                # 'paired_end': check_files[0],
                # 'single_end': check_files[1],
            })
        elif request.POST['paired_or_single'] == "single":
            myfile1 = request.FILES['s1']
            fs = FileSystemStorage()
            print("Checker path: ", os.path.join(
                settings.MEDIA_ROOT, project_name, "pe"))
            print("Checker path: ", os.path.join(
                settings.MEDIA_ROOT, project_name, "se"))
            if fs.exists(os.path.join(settings.MEDIA_ROOT, project_name, "pe")):
                print("Removing files")
                shutil.rmtree(os.path.join(
                    settings.MEDIA_ROOT, project_name, "pe"))
            if fs.exists(os.path.join(settings.MEDIA_ROOT, project_name, "se")):
                print("Removing files")
                shutil.rmtree(os.path.join(
                    settings.MEDIA_ROOT, project_name, "se"))
            filename1 = fs.save(os.path.join(
                project_name, "se", myfile1.name), myfile1)
            uploaded_file_url_se = fs.url(filename1)
            print("uploaded_file_url_se: ", uploaded_file_url_se)
            # return HttpResponseRedirect(request.path_info, {
            #     'single_end': check_files[1],
            #     'uploaded_file_url_1': uploaded_file_url_1,
            # })
            return render(request, "dataanalysis/home.html", {
                'which': "single-end",
                'project_name': project_name,
                'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
                'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
                'uploaded_file_url_se': uploaded_file_url_se,
                # 'paired_end': check_files[0],
                # 'single_end': check_files[1],
            })
    # return HttpResponseRedirect(request.path_info, {
    #     'paired_end': check_files[0],
    #     'single_end': check_files[1],
    # })
    return render(request, "dataanalysis/home.html", {
        'which': "normal",
        'project_name': project_name,
        'uploaded_file_url_pe_1': uploaded_file_url_pe_1,
        'uploaded_file_url_pe_2': uploaded_file_url_pe_2,
        'uploaded_file_url_se': uploaded_file_url_se,
    })

    #     form = PairedEndForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('dataanalysis_home')
    # else:
    #     form = PairedEndForm()
    # return render(request, 'dataanalysis/home.html', {
    #     'form': form,
    # })



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


def Check_Uploaded_File_Name(project_name):
    uploaded_file_url_pe_1 = None
    uploaded_file_url_pe_2 = None
    uploaded_file_url_se = None
    pe_files = []
    se_files = []
    upload_dir_pe = os.path.join(
        settings.MEDIA_ROOT, project_name, "pe")
    if os.path.exists(upload_dir_pe):
        pe_files = os.listdir(upload_dir_pe)
        print(pe_files)
        for file_check in pe_files:
            print(file_check)
            if ".R1.fastq" in file_check:
                uploaded_file_url_pe_1 = os.path.join(
                    "/media", project_name, "pe", file_check)
            if ".R2.fastq" in file_check:
                uploaded_file_url_pe_2 = os.path.join(
                    "/media", project_name, "pe", file_check)
        print("uploaded_file_url_pe_1: ", uploaded_file_url_pe_1)
        print("uploaded_file_url_pe_2: ", uploaded_file_url_pe_2)
        # uploaded_file_url_pe_1 = os.path.join(upload_dir_pe, pe_files[0])
        # uploaded_file_url_pe_2 = os.path.join(upload_dir_pe, pe_files[1])
    upload_dir_se = os.path.join(
        settings.MEDIA_ROOT, project_name, "se")
    if os.path.exists(upload_dir_se):
        se_files = os.listdir(upload_dir_se)
        uploaded_file_url_se = os.path.join("/media", project_name, "se", se_files[0])

    # files = glob.glob(upload_dir)

    return (uploaded_file_url_pe_1, uploaded_file_url_pe_2, uploaded_file_url_se)

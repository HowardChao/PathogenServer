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
    if 'project_name' in request.session:
        project_name = request.session['project_name']
        print("project_name: ", project_name)
    if 'analysis_code' is request.session:
        analysis_code = request.session['analysis_code']
        print("analysis_code: ", analysis_code)

    if request.method == 'POST' :
        print("paired_or_single: ", request.POST['paired_or_single'])
        if request.POST['paired_or_single'] == "paired":
            # form = PairedEndForm(request.POST, request.FILES)
            # for f in request.FILES.getlist('file'):
            #     PairedEnd.objects.create(file=f)
            # if form.is_valid():
            #     form.save()
            myfile1 = request.FILES['r1']
            myfile2 = request.FILES['r2']
            fs = FileSystemStorage()

            if fs.exists(os.path.join(project_name, "pe")):
                fs.delete(os.path.join(project_name, "pe"))
            if fs.exists(os.path.join(project_name, "pe")):
                fs.delete(os.path.join(project_name, "pe"))
            filename1 = fs.save(os.path.join(project_name, "pe", myfile1.name), myfile1)
            filename2 = fs.save(os.path.join(project_name, "pe", myfile2.name), myfile2)
            uploaded_file_url_1 = fs.url(filename1)
            uploaded_file_url_2 = fs.url(filename2)
            return render(request, 'dataanalysis/home.html', {
                'uploaded_file_url_1': uploaded_file_url_1,
                'uploaded_file_url_2': uploaded_file_url_2,
            })

        elif request.POST['paired_or_single'] == "single":
            myfile1 = request.FILES['s1']
            fs = FileSystemStorage()
            if fs.exists(os.path.join(project_name, "se")):
                fs.delete(os.path.join(project_name, "se"))
            filename1 = fs.save(os.path.join(
                project_name, "se", myfile1.name), myfile1)
            uploaded_file_url_1 = fs.url(filename1)
            return render(request, 'dataanalysis/home.html', {
                'uploaded_file_url_1': uploaded_file_url_1,
            })
    return render(request, 'dataanalysis/home.html')

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

def Get_Uploaded_File_Name(is_paired_end):
    if is_paired_end:
        file_name_1 = None
        file_name_2 = None
        upload_dir = os.path.join(
            settings.MEDIA_ROOT, project_name, "reads", "pe", "*.fastq.gz")
        files = glob.glob(upload_dir)
        print("Pair-end files:", files)
        if len(files) == 2:
            return files
        elif len(files) == 0:
            return None
        else:
            return "invalid"
    else:
        file_name = None
        upload_dir = os.path.join(
            settings.MEDIA_ROOT, project_name, "reads", "se", "*.fastq.gz")
        files = glob.glob(upload_dir)
        print("Single-end files:", files)
        if len(files) == 1:
            return files
        elif len(files) == 0:
            return None
        else:
            return "invalid"

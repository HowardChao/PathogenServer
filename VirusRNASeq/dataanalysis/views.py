from django.core.cache import cache
from django.http import HttpResponse
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

from dataanalysis.models import Document
from dataanalysis.forms import DocumentForm


def home(request):
    documents = Document.objects.all()
    return render(request, 'dataanalysis/home.html', { 'documents': documents })

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        if 'tmp_project_id' in request.session:
            tmp_project_id = request.session['tmp_project_id']
        print(tmp_project_id)
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
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'dataanalysis/model_form_upload.html', {
        'form': form
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

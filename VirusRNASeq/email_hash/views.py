from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from email_hash import models
from email_hash import forms
import uuid
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import shutil
import dataanalysis
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

TMP_DIR = "/home/kuan-hao/Documents/bioinformatics/Virus/analysis_results/tmp_project"

def analysis_code_generator():
    return uuid.uuid1().hex

def project_name_generator():
    return "Project" + uuid.uuid1().hex

def newsletter_singup(request):
    default_analysis_code = analysis_code_generator()
    form = forms.NewsletterUserSignUpForm(
        initial={
            'analysis_code': default_analysis_code,
        }
    )
    print("$$$$$$$$$$: ", form)
    form = forms.NewsletterUserSignUpForm(request.POST or None)
    if form.is_valid():
        assembly_type = request.POST['assembly_type_get']
        instance = form.save(commit=False)
        instance.analysis_code = default_analysis_code
        instance.assembly_type_input = assembly_type
        instance.save()
        # print("$$$$$$$$$$: ", instance.assembly_type_input)
        user_project_number = models.NewsletterUser.objects.filter(email=instance.email).count()
        messages.warning(request, 'You have ' + str(user_project_number) + ' analysis project in VirusRNASeq', extra_tags="alert alert-warning alert-dismissible fade show")
        from_email = settings.EMAIL_HOST_USER
        to_email = [instance.email]
        messages.success(request, 'Your analysis project has been created. Project access id has been sent to  \'' + instance.email + '\'', extra_tags="alert alert-success alert-dismissible fade show")
        subject = "Thank you for using VrisuRNASeq"
        signup_message = """Welcome to VirusRNASeq!\nYour Project access id is:\n """ + str(instance.analysis_code) + """.   If you would like to delete your analysis process, visit http://127.0.0.1:8000/email_hash/delete_analysis"""
        send_mail(subject=subject, from_email=from_email, recipient_list=to_email, message=signup_message, fail_silently=False)
    context = {
        'form': form,
    }
    template = "email_hash/sign_up.html"
    return render(request, template, context)

def newsletter_unsubscribe(request):
    form = forms.NewsletterUserDeleteAnalysisForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        inside_or_outside = False
        if models.NewsletterUser.objects.filter(project_name=instance.project_name,email=instance.email, analysis_code=instance.analysis_code).exists():
            destination_QC_html_dir = os.path.join(os.path.dirname(dataanalysis.__file__), 'templates', 'dataanalysis', 'tmp', instance.project_name + '_' + instance.email + '_' + instance.analysis_code)
            if os.path.exists(destination_QC_html_dir):
                print("destination_QC_html_dir: ", destination_QC_html_dir)
                shutil.rmtree(destination_QC_html_dir)
            inside_or_outside = True
            print("You successfully delete your project!")
            base_dir = os.path.join(settings.MEDIA_ROOT,
                                    'tmp', instance.project_name + '_' + instance.email + '_' + instance.analysis_code)
            models.NewsletterUser.objects.filter(
                project_name=instance.project_name, email=instance.email, analysis_code=instance.analysis_code).delete()
            fs = FileSystemStorage()
            if fs.exists(base_dir):
                shutil.rmtree(base_dir)
            messages.success(request, 'Your analysis project has been removed from database. Thank you for using VirusRNASeq!',
                             extra_tags="alert alert-success alert-dismissible fade show")
        else:
            inside_or_outside = False
            print(inside_or_outside)
            messages.warning(request, 'Your analysis project is not found in the database!',
                             extra_tags="alert alert-warning alert-dismissible fade show")
    context = {
        "form": form,
    }
    template = "email_hash/unsubscribe.html"
    return render(request, template, context)

def check_project(request):
    form = forms.NewsletterUserCheck(request.POST or None)
    inside_or_outside = False
    project_name = "None"
    email = "None"
    url_parameter = "None"
    assembly_type_input = "None"
    if form.is_valid():
        instance = form.save(commit=False)
        if models.NewsletterUser.objects.filter(analysis_code=instance.analysis_code).exists():
            query_instance = models.NewsletterUser.objects.get(analysis_code=instance.analysis_code)
            project_name = query_instance.project_name
            analysis_code = instance.analysis_code
            email = query_instance.email
            assembly_type_input = query_instance.assembly_type_input
            url_parameter = project_name + '_' + email.split("@")[0]
            print("project_name: ", project_name)
            print("analysis_code: ", analysis_code)
            print("email: ", email)
            # request.session['tmp_project_id'] = instance.project_name
            inside_or_outside = True
            request.session["project_name"] = project_name
            request.session["analysis_code"] = analysis_code
            request.session["email"] = email
            request.session["assembly_type_input"] = assembly_type_input
            upload_dir = os.path.join(
                settings.MEDIA_ROOT, project_name, "reads")
            print("***Upload_dir id: ", upload_dir)
            # if not os.path.exists(upload_dir):
            #     os.makedirs(upload_dir)
            messages.success(request, 'Your analysis code is correct!',
                             extra_tags="alert alert-success alert-dismissible fade show")
        else:
            inside_or_outside = False
            messages.warning(request, 'Your analysis code is not correct try again!',extra_tags="alert alert-warning alert-dismissible fade show")
    variable = {
        "inside_or_outside": inside_or_outside,
        "project_name": project_name,
        "email": email,
        "assembly_type_input": assembly_type_input,
        "url_parameter": url_parameter,
    }
    context = {
        "variable": variable,
        "form": form,
    }
    template = "email_hash/check_project.html"
    return render(request, template, context)

def help_view(request):
    template = "email_hash/help.html"
    return render(request, template)

def about_view(request):
    template = "email_hash/about.html"
    return render(request, template)

def merge_project(request):
    template = "email_hash/merge_project.html"
    return render(request, template)

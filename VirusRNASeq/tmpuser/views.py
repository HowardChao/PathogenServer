from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import TmpUserRegisterForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import uuid
import os

def analysis_code_generator():
    return uuid.uuid1().hex

def start_new_project(request):
    if request.method == 'POST':
        form = TmpUserRegisterForm(request.POST)
        if form.is_valid():
            password = analysis_code_generator()
            # post = request.POST.copy()  # to make it mutable
            print("Password: ", password)
            # form.cleaned_data['password1'] = password
            # form.cleaned_data['password2'] = password
            # form.cleaned_data['username'] = "tmp_user"
            # post['username'] = "tmp_user"
            # post['password1'] = password
            # post['password2'] = password
            form.save()
            email = form.cleaned_data['email']
            user_project_number = User.objects.filter(
                email=email).count()
            messages.warning(request, 'You have ' + str(user_project_number) + 'analysis project in VirusRNASeq', extra_tags="alert alert-warning alert-dismissible fade show")
            from_email = settings.EMAIL_HOST_USER
            to_email = [email]
            messages.success(request, 'Your analysis project has been created. Project access id has been sent to  \'' +
                             email + '\'. You are now able to check your analysis.', extra_tags="alert alert-success alert-dismissible fade show")
            subject = "Thank you for using VrisuRNASeq"
            signup_message = """Welcome to VirusRNASeq!\nYour Project access id is:\n """ + \
                str(password) + \
            """.   If you would like to delete your analysis process, visit http://127.0.0.1:8000/email_hash/delete_analysis"""
            send_mail(subject=subject, from_email=from_email,
                  recipient_list=to_email, message=signup_message, fail_silently=False)
        context = {
            'form': form,
        }
        template = "tmpuser/start_new_project.html"
        return render(request, template, context)
    else:
        form = TmpUserRegisterForm()
    return render(request, 'tmpuser/start_new_project.html', {'form': form})


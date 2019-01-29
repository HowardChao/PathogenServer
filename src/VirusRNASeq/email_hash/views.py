from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from email_hash import models
from email_hash import forms

def newsletter_singup(request):
    form = forms.NewsletterUserSignUpForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if models.NewsletterUser.objects.filter(email=instance.email).exists():
            messages.warning(request, 'Your Email Already exist in our database', extra_tags="alert alert-warning alert-dismissible fade show")
        else:
            instance.save()
            messages.success(request, 'Your Email has been submitted to database',
                             extra_tags="alert alert-success alert-dismissible fade show")
            subject = "Thank you for using VrisuRNASeq"
            from_email = settings.EMAIL_HOST_USER
            to_email = [instance.email]
            signup_message = """Welcome to VirusRNASeq! If you would like to delete your analysis process, visit http://127.0.0.1:8000/email_hash/unsubscribe"""
            send_mail(subject=subject, from_email=from_email, recipient_list=to_email, message=signup_message, fail_silently=False)
            

    context = {
        'form': form,
    }
    template = "email_hash/sign_up.html"
    return render(request, template, context)

def newsletter_unsubscribe(request):
    form = forms.NewsletterUserSignUpForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        if models.NewsletterUser.objects.filter(email=instance.email).exists():
            models.NewsletterUser.objects.filter(email=instance.email).delete()
            messages.success(request, 'Your Email has been removed',
                             extra_tags="alert alert-success alert-dismissible fade show")
        else:
            messages.warning(request, 'Your Email is not in the database',
                             extra_tags="alert alert-warning alert-dismissible fade show")
        
    context = {
        "form": form,
    }
    template = "email_hash/unsubscribe.html"
    return render(request, template, context)

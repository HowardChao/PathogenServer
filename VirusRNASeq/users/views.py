from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, TmpUserRegisterForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import uuid

def analysis_code_generator():
    return uuid.uuid1().hex

def project_name_generator():
    return "Project" + uuid.uuid1().hex

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def start_new_project(request):

    # form = TmpUserRegisterForm(initial={
    #     'email': 'ck1021051@gmail.com',
    #     'password2': password,
    #     'password1': password,
    #     'username': username})
    # form.fields['email'].widget.render_value = True
    # form.fields['password2'].widget.render_value = True
    template = "users/start_new_project.html"
    if request.method == 'POST':
        username = project_name_generator()
        password = User.objects.make_random_password()
        # password = analysis_code_generator()
        # post = request.POST.copy()  # to make it mutable
        # post['username'] = username
        # post['password1'] = password
        # post['password2'] = password
        form = TmpUserRegisterForm(request.POST)
        if form.is_valid():
            print("username: ", username)
            print("Password: ", password)
            # form.cleaned_data['username'] = "qwertyuioop"
            # form.cleaned_data['password1'] = password
            # form.cleaned_data['password2'] = password
            # instance = form.save(commit=False)
            form.save()
            # instance.username = username
            # instance.password1 = password
            # instance.password2 = password
            email = form.cleaned_data['email']
            user_project_number = User.objects.filter(
                email=email).count()
            messages.warning(request, 'You have ' + str(user_project_number) + 'analysis project in VirusRNASeq',
                             extra_tags="alert alert-warning alert-dismissible fade show")
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
        return render(request, template, context)
    else:
        form = TmpUserRegisterForm()
    return render(request, template, {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES,instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(
                request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context=context)


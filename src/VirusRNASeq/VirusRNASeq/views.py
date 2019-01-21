from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

def home(request):
    return render(request, 'index.html')
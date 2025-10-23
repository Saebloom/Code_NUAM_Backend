from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def miapp(request):
    return HttpResponse("<BR>Hello world!</BR>")

def acercade(request):
    return render(request, 'acercade.html')
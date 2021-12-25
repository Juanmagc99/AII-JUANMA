from django.shortcuts import render
from principal import populateDB

# Create your views here.

def inicio(request):
    return render(request,'index.html')

def populate(request):
    populateDB.populate()
    return render(request,'index.html')

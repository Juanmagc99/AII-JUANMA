from django.shortcuts import render
from principal import populateDB
from principal.form import JobTitleForm

# Create your views here.

def inicio(request):
    return render(request,'index.html')

def populate(request):
    populateDB.populateDB()
    return render(request,'index.html')

def whooshLoad(request):
    populateDB.cargaWhoosh()
    return render(request,'index.html')

def searchByTitle(request):
    if request.method=='GET':
        form = JobTitleForm(request.GET)
        if form.is_valid():
            return None
    form = JobTitleForm()
    return render(request,'search_job_title.html', {'form': form})
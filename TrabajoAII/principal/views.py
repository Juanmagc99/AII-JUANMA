from django.shortcuts import render
from principal.models import Job
from principal import populateDB
from principal.form import JobMultifieldForm,JobSkillsForm
from whoosh import query
import re, os, shutil
from whoosh.qparser import QueryParser, OrGroup, MultifieldParser
from whoosh.index import create_in,open_dir

# Create your views here.

def inicio(request):
    return render(request,'index.html')

def populate(request):
    populateDB.populateDB()
    return render(request,'index.html')


def listJobs(request):
    jobs = Job.objects.all().values()
    return render(request,'index.html', {'jobs': jobs})

def searchByMultipleField(request):
    if request.method=='POST':
        form = JobMultifieldForm(request.POST)
        if form.is_valid():
            keywords = form.cleaned_data['keywords']
            avalible = form.cleaned_data['salary_avalible']
            location = form.cleaned_data['location']
            print(avalible)
            ix = open_dir('Index')
            with ix.searcher() as searcher:
                print(location)
                query_loc = QueryParser('location', ix.schema, group=OrGroup).parse(str(location))
                query_key = MultifieldParser(["title","description"], ix.schema, group=OrGroup).parse(str(keywords))
                results = searcher.search(query_key, limit=20)
                results_loc = searcher.search(query_loc, limit=30)
                results.upgrade_and_extend(results_loc)
                print(results)
                l = []
                for r in results:
                    if(avalible and '£' in r['salary']):
                        l.append([r['title'], r['location'], r['salary'], r['url']])
                    elif(not avalible):
                        l.append([r['title'], r['location'], r['salary'], r['url']])
            return render(request,'index.html', {'jobs_whoosh': l})
    form = JobMultifieldForm()
    return render(request,'search_job.html', {'form': form})

def searchBySkills(request):
    if request.method == 'POST':
        return None
    
    form = JobSkillsForm()
    return render(request,'search_job.html', {'form':form})
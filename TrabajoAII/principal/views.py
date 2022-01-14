from django.shortcuts import render, get_object_or_404
from principal.models import Job,Tag,Rating
import shelve
from principal import populateDB
from principal.form import JobMultifieldForm,JobSkillsForm, JobSimilar
from principal.recommendations import  transformPrefs, getRecommendations, topMatches
from whoosh import query
import re, os, shutil
from whoosh.qparser import QueryParser, OrGroup, MultifieldParser
from whoosh.index import create_in,open_dir

# Create your views here.

def create_dic(request):
    Prefs={}
    shelf = shelve.open("dataRS.dat")
    ratings = Rating.objects.all()
    for ra in ratings:
        job = int(ra.job.id)
        tag = int(ra.tag.id)
        rating = int(ra.included)
        Prefs.setdefault(job, {})
        Prefs[job][tag] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf.close()
    return render(request,'index.html')

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
                l = []
                for r in results:
                    if(avalible and '£' in r['salary']):
                        l.append([r['title'], r['location'], r['salary'], r['url']])
                    elif(not avalible):
                        l.append([r['title'], r['location'], r['salary'], r['url']])
            ix.close()
            return render(request,'index.html', {'jobs_whoosh': l})
    form = JobMultifieldForm()
    return render(request,'search_job.html', {'form': form})

def searchBySkills(request):
    if request.method == 'POST':
        form = JobSkillsForm(request.POST)
        if form.is_valid():
            skills = form.cleaned_data['skills']
            ix = open_dir('Index')
            skills_str = ''
            for s in skills.values():
                skills_str += (' ' + s['value'])
            skills_str.replace(',', '')
            with ix.searcher() as searcher:
                query = QueryParser('tags', ix.schema,group=OrGroup).parse(skills_str)
                results = searcher.search(query, limit=20)
                l = []
                for r in results:
                    l.append([r['title'], r['location'], r['salary'], r['url']])
        ix.close()
        return render(request,'index.html', {'jobs_whoosh': l})
    form = JobSkillsForm()
    return render(request,'search_job.html', {'form':form})


def recommendedJob(request):
    film = None
    if request.method=='POST':
        form = JobSimilar(request.POST)
        if form.is_valid():
            idFilm = form.cleaned_data['id']
            film = get_object_or_404(Job, pk=idFilm)
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['ItemsPrefs']
            shelf.close()
            recommended = topMatches(Prefs, int(idFilm),n=3)
            films = []
            similar = []
            for re in recommended:
                films.append(Job.objects.get(pk=re[1]))
                similar.append(re[0])
            items= zip(films,similar)
            return render(request,'index.html', {'items': items})
    form = JobSimilar()
    print(Tag.objects.all().values())
    print(Job.objects.all().values())
    return render(request,'search_job.html', {'form': form})
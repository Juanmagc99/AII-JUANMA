
from bs4 import BeautifulSoup
import urllib.request
import re, os, shutil
from principal.models import Job, Tag
from whoosh import query
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.qparser import QueryParser

def populate():
    Job.objects.all().delete()
    num = 0
    d = {}
    d_num = 0
    for i in range(1,10):
        f1 = urllib.request.urlopen("https://www.reed.co.uk/jobs/it-jobs?pageno="+str(i)+"&sortby=DisplayDate")
        s1 = BeautifulSoup(f1, 'lxml')
        
        for j in s1.find_all('article', attrs={'class':'job-result'}):
            url = " https://www.reed.co.uk" + j.find('a', attrs={'class':'job-block-link'})['href']
            offer = j.find('label', attrs={'class':'label-promoted'})
           
            if(offer == None):
               
                f2 = urllib.request.urlopen(url)
                s2 = BeautifulSoup(f2, 'lxml')
                skills = s2.find('ul', attrs={'class':'skills-list'})
                if(skills):
                    print(url)
                    num+=1
                    title = s2.find('header', attrs={'class':'job-header'}).find('h1').string.strip()
                    print(title)
                
                    details = s2.find('div', attrs={'class':['metadata','container']})
                
                    salary = details.find('span', attrs={'data-qa':'salaryMobileLbl'}).string.strip()
                    print("Salary: " + salary)
                    
                    city = details.find('span', attrs={'data-qa':'localityMobileLbl'}).string.strip()
                    region = details.find('span', attrs={'data-qa':'regionMobileLbl'})
                    if(region):
                        location = city + ", " + region.string.strip()
                    else:
                        location = city
                    
                    print("Location: " + location)
                    type = ''.join(details.find('span', attrs={'data-qa':'jobTypeMobileLbl'}).stripped_strings)
                    print('Type: ' + type)

                    job = Job(title=title, location=location, salary=salary, type=type)
                    job.save()

                    for s in skills.find_all('li'):
                        if( s.text not in d.values()):
                            tag = Tag(value = s.text)
                            tag.save()
                            d[d_num] = s.text
                            job.tags.add(tag)
                            d_num += 1
                        else:
                            job.tags.add(Tag.objects.get(value = s.text))
                    
                    print("\n\n +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return d

def deleteTables():
    Job.objects.all().delete()
    Tag.objects.all().delete()

def cargaWhoosh():
    '''Creamos el esquema de los datos que vamos a guardar, se usa ID cuando se sabe que sera único'''
    schema = Schema(title=TEXT(stored=True), location=TEXT(stored=True), salary=TEXT(stored=True), 
    type=KEYWORD(stored=True, commas=True, lowercase=True), tags=KEYWORD(stored=True, commas=True, lowercase=True))

    '''En caso de existir el directorio de indice lo borramos y creamos de nuevo'''
    if os.path.exists('Index'):
        shutil.rmtree('Index')
    os.mkdir('Index')
    
    '''Se crea el indice dentro del directorio anterior'''
    ix = create_in('Index', schema=schema)

    writer = ix.writer()
    i = 0
    lista = Job.objects.all().values()
    for n in lista:
        writer.add_document(title=str(n['title']), location=str(n['location']), salary=str(n['salary']), type=str(n['type']))
        i+=1
    
    writer.commit()


def populateDB():
    deleteTables()
    d = populate()
    

    
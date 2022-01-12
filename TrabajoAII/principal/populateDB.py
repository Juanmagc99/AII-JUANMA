
from bs4 import BeautifulSoup
import datetime
import urllib.request
import re, os, shutil
from principal.models import Job, Tag
from whoosh import query
from whoosh.index import create_in,open_dir
from whoosh.fields import DATETIME, Schema, TEXT, KEYWORD
from whoosh.qparser import QueryParser

def populate():

    '''Creamos el esquema de los datos que vamos a guardar, se usa ID cuando se sabe que sera único'''
    schema = Schema(title=TEXT(stored=True), location=TEXT(stored=True), salary=TEXT(stored=True), description=TEXT(stored=False),
    type=KEYWORD(stored=True, commas=True, lowercase=True), tags=KEYWORD(stored=True, commas=True, lowercase=True)
    , url=TEXT(stored=True))

    '''En caso de existir el directorio de indice lo borramos y creamos de nuevo'''
    if os.path.exists('Index'):
        shutil.rmtree('Index')
    os.mkdir('Index')

    '''Se crea el indice dentro del directorio anterior'''
    ix = create_in('Index', schema=schema)
    writer = ix.writer()

    num = 0
    d = {}
    d_num = 0
    for i in range(1,):
        f1 = urllib.request.urlopen("https://www.reed.co.uk/jobs/it-jobs?pageno="+str(i)+"&sortby=DisplayDate")
        #f1 = urllib.request.urlopen("https://www.reed.co.uk/jobs?pageno="+str(i)+"&multipleparentsectorids=52%2C68%2C12%2C5%2C2&sortby=DisplayDate")
        s1 = BeautifulSoup(f1, 'lxml')
        
        for j in s1.find_all('article', attrs={'class':'job-result'}):
            url = "https://www.reed.co.uk" + j.find('a', attrs={'class':'job-block-link'})['href']
            f2 = urllib.request.urlopen(url)
            s2 = BeautifulSoup(f2, 'lxml')
            skills = s2.find('ul', attrs={'class':'skills-list'})
            banner = s2.find('img', attrs={'id':'bannerImageJob'})
            if(skills != None and banner == None):
                print(url)
                num+=1
                
                publication = s2.find('span', attrs={'itemprop':'hiringOrganization'}).text.replace('Posted ', '').split(' by ')[0].strip()
                print(publication)

                title = s2.find('header', attrs={'class':'job-header'}).find('h1').string.strip()
                
                details = s2.find('div', attrs={'class':['metadata','container']})
            
                salary = details.find('span', attrs={'data-qa':'salaryMobileLbl'}).string.strip()
                
                city = details.find('span', attrs={'data-qa':'localityMobileLbl'}).string.strip()
                region = details.find('span', attrs={'data-qa':'regionMobileLbl'})
                if(region):
                    location = city + ", " + region.string.strip()
                else:
                    location = city
                
                description = s2.find('span', attrs={'itemprop':'description'})

                type = ''.join(details.find('span', attrs={'data-qa':'jobTypeMobileLbl'}).stripped_strings)
                
                job = Job(title=title, location=location, salary=salary, type=type, url=url)
                job.save()
                tags_str = ''
                for s in skills.find_all('li'):
                    if( s.text not in d.values()):
                        tag = Tag(value = s.text)
                        tag.save()
                        d[d_num] = s.text
                        job.tags.add(tag)
                        d_num += 1
                        tags_str += str(s.text) + ','
                    else:
                        job.tags.add(Tag.objects.get(value = s.text))
                        tags_str += str(s.text) + ','

                tags_str[0:-1].replace(' / ',',')
                if(description):
                    writer.add_document(title=str(title), location=str(location), salary=str(salary), type=str(type), tags=tags_str,
                     description=description.text,url=url)
                else:
                    writer.add_document(title=str(title), location=str(location), salary=str(salary), type=str(type), tags=tags_str
                    ,url=url)


                print(title)
                print("Salary: " + salary)
                print("Location: " + location)
                print('Type: ' + type)
                print("\n\n +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    
    writer.commit()
    return d

def deleteTables():
    Job.objects.all().delete()
    Tag.objects.all().delete()

def populateDB():
    deleteTables()
    d = populate()
    

    
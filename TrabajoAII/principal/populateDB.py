
from bs4 import BeautifulSoup
import urllib.request
import re
from principal.models import Job

def populate():
    Job.objects.all().delete()

    for i in range(1,2):
        f1 = urllib.request.urlopen("https://www.reed.co.uk/jobs/it-jobs?pageno="+str(i)+"&sortby=DisplayDate")
        s1 = BeautifulSoup(f1, 'lxml')
        for j in s1.find_all('article', attrs={'class':'job-result'}):
            url = " https://www.reed.co.uk" + j.find('a', attrs={'class':'job-block-link'})['href']
            f2 = urllib.request.urlopen(url)
            s2 = BeautifulSoup(f2, 'lxml')
            
            title = s2.find('header', attrs={'class':'job-header'}).find('h1').string.strip()
            print("Title: " + title)
            
            details = s2.find('div', attrs={'class':['metadata','container']})
            #print(details)
            
            salary_aux = details.find('span', attrs={'data-qa':'salaryMobileLbl'}).string.strip()
            print("Salary: " + salary_aux)
            
            city = details.find('span', attrs={'data-qa':'localityMobileLbl'}).string.strip()
            region = details.find('span', attrs={'data-qa':'regionMobileLbl'}).string.strip()
            location = city + ", " + region
            print("Location: " + location)


            print("\n\n +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            


            
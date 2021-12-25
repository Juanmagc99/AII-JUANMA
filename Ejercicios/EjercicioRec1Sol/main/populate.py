from main.models import Libro, Puntuacion
from datetime import datetime

path = "goodreads-dataset"

def deleteTables():
    Puntuacion.objects.all().delete()
    Libro.objects.all().delete()
    Puntuacion.objects.all().delete()
  
    
'''def populateOccupations():
    print("Loading occupations...")
        
    lista=[]
    fileobj=open(path+"\\u.occupation", "r")
    for line in fileobj.readlines():
        lista.append(Occupation(occupationName=str(line.strip())))
    fileobj.close()
    Occupation.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    print("Occupations inserted: " + str(Occupation.objects.count()))
    print("---------------------------------------------------------")


def populateUsers():
    print("Loading users...")
       
    lista=[]
    dict={}
    fileobj=open(path+"\\u.user", "r")
    for line in fileobj.readlines():
        rip = line.split('|')
        if len(rip) != 5:
            continue
        id_u=int(rip[0].strip())
        u=UserInformation(id=id_u, age=rip[1].strip(), gender=rip[2].strip(), occupation=Occupation.objects.get(occupationName=rip[3].strip()), zipCode=rip[4].strip())
        lista.append(u)
        dict[id_u]=u
    fileobj.close()
    UserInformation.objects.bulk_create(lista)
    
    print("Users inserted: " + str(UserInformation.objects.count()))
    print("---------------------------------------------------------")
    return(dict)'''


def populateBooks():
    print("Loading books...")
       
    lista_books = []
    dict={}
    fileobj=open(path+"\\u.item", "r")
    for line in fileobj.readlines():
        rip = line.split('|')
        id_book = int(rip[0].strip())
        b = Libro(id=id_book, title = rip[1].strip(), author = rip[2].strip(), genre = rip[3].strip(), language = rip[4].strip())
        lista_books.append(b)
        dict[id_book] = b      
    fileobj.close()    
    Libro.objects.bulk_create(lista_books)
    
    print("Books inserted: " + str(Libro.objects.count()))
    print("---------------------------------------------------------")
    return(dict)
       
def populateRatings(b):
    print("Loading ratings...")
    Puntuacion.objects.all().delete()

    lista=[]
    fileobj=open(path+"\\ratings.csv", "r")
    for line in fileobj.readlines():
        rip = line.split('\t')
        lista.append(Puntuacion(user=int(rip[1].strip()), book=b[int(rip[2].strip())], score=int(rip[0].strip())))
    fileobj.close()
    Puntuacion.objects.bulk_create(lista)
    print("Ratings inserted: " + str(Puntuacion.objects.count()))
    print("---------------------------------------------------------")
    
    
def populateDatabase():
    deleteTables()
    b=populateBooks()
    populateRatings(b)
    print("Finished database population")
    
if __name__ == '__main__':
    populateDatabase()
#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh import query
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, ID
from whoosh.qparser import QueryParser

# lineas para evitar error SSL
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extraer_noticias():
    
    lista_noticias = []

    for i in range(1,4):
        l_pagina = []

        f = urllib.request.urlopen("https://www.meneame.net/?page="+str(i))
        s = BeautifulSoup(f, 'lxml')
        l = s.find_all('div', class_='center-content')
        for i in l:
            titulo = i.h2.a.string
            autor = i.div.find_all('a')[1].string
            
            fuente_link = i.find('span', class_='showmytitle')
            if fuente_link:
                fuente = fuente_link.string
                link = fuente_link['title']
            else:
                fuente = 'Anonima'
                link = 'Desconocido'
           
            fecha_exists = i.find('span', {'data-ts':True, 'title':re.compile("publicado")})
            if i.find('span', {'data-ts':True, 'title':re.compile("publicado")}):
                fecha_ts = fecha_exists['data-ts']
            else:
                fecha_ts = i.find('span', {'data-ts':True, 'title':re.compile("enviado")})['data-ts']
            fecha = datetime.fromtimestamp(int(fecha_ts))

            contenido = i.find('div', class_='news-content').text

            l_pagina.append((titulo, autor, fuente, link, fecha, contenido))
        
        lista_noticias.extend(l_pagina)

    return lista_noticias

            
def cargar_datos():
    '''Creamos el esquema de los datos que vamos a guardar, se usa ID cuando se sabe que sera único'''
    schema = Schema(titulo=TEXT(stored=TRUE), autor=TEXT(stored=TRUE), fuente=TEXT(stored=TRUE), 
    link=ID(stored=TRUE), fecha=DATETIME(stored=TRUE), contenido=TEXT)

    '''En caso de existir el directorio de indice lo borramos y creamos de nuevo'''
    if os.path.exists('Index'):
        shutil.rmtree('Index')
    os.mkdir('Index')
    
    '''Se crea el indice dentro del directorio anterior'''
    ix = create_in('Index', schema=schema)

    writer = ix.writer()
    i = 0
    lista = extraer_noticias()
    for n in lista:
        writer.add_document(titulo=str(n[0]), autor=str(n[1]), fuente=str(n[2]), link=str(n[3])
        , fecha=n[4], contenido=str(n[5]))
        i+=1
    writer.commit()

    messagebox.showinfo('Fin de indexado', 'Se han indexado '+str(i)+' noticias')

def buscar_contenido():
    def mostrar_lista(event):
        #Abrimos indice
        ix = open_dir("Index")
        #Se crea un search para navegar a traves del indice
        with ix.searcher() as searcher:
            query = QueryParser('contenido', ix.schema).parse(str(en.get()))
            results = searcher.search(query)
            
            v = Toplevel()
            v.title("Listado de Noticias")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill=BOTH)
            sc.config(command=lb.yview)

            for r in results: 
                lb.insert(END,r['titulo'])
                lb.insert(END,r['autor'])
                lb.insert(END,r['link'])
                lb.insert(END,r['fecha'])
                lb.insert(END,'')

    
    v = Toplevel()
    v.title("Busqueda por Noticia")
    l = Label(v, text='Introduzca palabra clave:')
    en = Entry(v)
    en.bind('<Return>', mostrar_lista)
    en.pack(side=LEFT)

def buscar_fuente():
    def mostrar_lista(event):
        #Abrimos indice
        ix = open_dir("Index")
        #Se crea un search para navegar a traves del indice
        with ix.searcher() as searcher:
            query = QueryParser('fuente', ix.schema).parse(str(en.get()))
            results = searcher.search(query)
            
            v = Toplevel()
            v.title("Listado de Noticias")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill=BOTH)
            sc.config(command=lb.yview)

            for r in results: 
                lb.insert(END,r['titulo'])
                lb.insert(END,r['autor'])
                lb.insert(END,r['fuente'])
                lb.insert(END,'')

    
    v = Toplevel()
    v.title("Busqueda por fuente")
    l = Label(v, text='Introduzca fuente:')
    en = Entry(v)
    en.bind('<Return>', mostrar_lista)
    en.pack(side=LEFT)


def ventana_principal():

    app = Tk()
    menu = Menu(app)

    #DATOS
    datosMenu = Menu(menu, tearoff=0)
    datosMenu.add_command(label='Cargar datos', command=cargar_datos)
    datosMenu.add_command(label='Salir', command=app.quit)
    menu.add_cascade(label='Datos', menu=datosMenu)

    #BUSQUEDA
    buscarMenu = Menu(menu, tearoff=0)
    buscarMenu.add_command(label='Buscar contenido', command=buscar_contenido)
    buscarMenu.add_command(label='Buscar fuente', command=buscar_fuente)
    menu.add_cascade(label='Buscar', menu=buscarMenu)

    app.config(menu=menu)
    app.mainloop()

if __name__ == '__main__':
    ventana_principal()
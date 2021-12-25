#encoding:utf-8
 
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
import datetime
import locale
from datetime import date    
locale.setlocale(locale.LC_TIME, "es_ES")
 
# lineas para evitar error SSL
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
 
def extraer_noticias():
    locale.setlocale(locale.LC_TIME, "es_ES")
    lista_noticias = []
    for i in range(1,3):
        f = urllib.request.urlopen('https://www.sensacine.com/noticias/?page='+str(i))
        s = BeautifulSoup(f, 'lxml')
 
        datos = s.find('section', class_="section section-wrap gd-2-cols gd-gap-30 row-col-sticky").find_all('div', class_='news-card')
        noticias = []
        for c in datos:
            titulo = c.find('a', class_='meta-title-link').string.strip()
            resumen = c.find('div', class_='meta-body')
            if resumen == None:
                resumen = 'No disponible'
            else:
                resumen = resumen.string.strip()
            fecha_strp = c.find('div', class_='meta-date').string.strip().split(', ')
            fecha = datetime.datetime.strptime(fecha_strp[1], "%d de %B de %Y")
            cat = c.find('div', class_='meta-category').string.strip().split(' - ')
            categoria = cat[1].lower()
            noticias.append((fecha, titulo, resumen, categoria))
       
        lista_noticias.extend(noticias)
    return lista_noticias
           
 
def cargar():
    schem = Schema(fecha=DATETIME(stored=True), titulo=TEXT(stored=True), resumen=TEXT(stored=True),categoria=TEXT(stored=True))
 
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
 
    ix = create_in("Index", schema=schem)
    writer = ix.writer()
    i=0
    lista = extraer_noticias()
   
    for n in lista:
        writer.add_document(fecha=n[0], titulo=str(n[1]), resumen=str(n[2]), categoria=str(n[3]))
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " noticias")  
 
def buscar_titulo():
    def mostrar_lista(event):
        ix = open_dir('Index')
        with ix.searcher() as searcher:
            query = QueryParser("titulo", ix.schema).parse(str(en.get()))
            results = searcher.search(query)
            print(results)
            v = Toplevel()
            v.title("Listado de noticias")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            #Importante: el diccionario solo contiene los campos que han sido almacenados(stored=True) en el Schema
            for r in results:
                lb.insert(END,r["categoria"])
                lb.insert(END,r["fecha"])
                lb.insert(END,r["titulo"])
                lb.insert(END,'')
 
    v = Toplevel()
    v.title("Busqueda de noticias")
    l = Label(v, text="Introduzca palabra titulo:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
 
def buscar_titulo_resumen():
    def mostrar_lista(event):
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            query = MultifieldParser(["titulo","resumen"], ix.schema, group=OrGroup).parse(str(en.get()))
            results = searcher.search(query)
 
 
            v = Toplevel()
            v.title("Listado de Noticias")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            #Importante: el diccionario solo contiene los campos que han sido almacenados(stored=True) en el Schema
            for r in results:
                lb.insert(END,r['categoria'])
                lb.insert(END,r['fecha'])
                lb.insert(END,r['titulo'])
                lb.insert(END,r['resumen'])
                lb.insert(END,'')
   
    v = Toplevel()
    v.title("Busqueda")
    l = Label(v, text="Introduzca:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
 
def buscar_fecha():
   def mostrar_lista(event):
       ix=open_dir("Index")
       if(not re.match("\d{2} \D{3} \d{4}",en.get())):
           messagebox.showinfo("Error", "Formato de fecha incorrecto (debe ser dd MMMM aaaa)")
           return
       with ix.searcher() as searcher:
           d = {'jan':'01', 'feb':'02', 'mar':'03', 'apr':'04', 'may':'05', 'jun':'06', 'jul':'07',
           'aug':'08', 'sep':'09', 'oct':'10', 'nov':'11', 'dec':'12'}
           fecha_splt = en.get().split()
           fecha_correct = fecha_splt[2] + d.get(fecha_splt[1]) + fecha_splt[0]
           print(fecha_correct)
           print(en.get())
           print(date.today().strftime("%Y%m%d"))
           rango_fecha = '['+ fecha_correct + ' TO ' + date.today().strftime("%Y%m%d") +']'
           query = QueryParser("fecha", ix.schema).parse(rango_fecha)
           results = searcher.search(query)
           v = Toplevel()
           v.title("Listado de noticias")
           v.geometry('800x150')
           sc = Scrollbar(v)
           sc.pack(side=RIGHT, fill=Y)
           lb = Listbox(v, yscrollcommand=sc.set)
           lb.pack(side=BOTTOM, fill = BOTH)
           sc.config(command = lb.yview)
           #Importante: el diccionario solo contiene los campos que han sido almacenados(stored=True) en el Schema
           for r in results:
               lb.insert(END,r["categoria"])
               lb.insert(END,r["fecha"])
               lb.insert(END,r["titulo"])
               lb.insert(END,'')
 
   v = Toplevel()
   v.title("Busqueda de noticias")
   l = Label(v, text="Introduzca fecha (dd MMM aaaa):")
   l.pack(side=LEFT)
   en = Entry(v)
   en.bind("<Return>", mostrar_lista)
   en.pack(side=LEFT)
 
def buscar_categoria():
   def mostrar_lista(event):
       if (not str(en.get()) in categorias):
            messagebox.showinfo("Error", "Debe ser una categoria correcta")
            return
       with ix.searcher() as searcher:
           query = QueryParser("categoria", ix.schema).parse(str(en.get()))
           results = searcher.search(query)
           v = Toplevel()
           v.title("Listado de noticias")
           v.geometry('800x150')
           sc = Scrollbar(v)
           sc.pack(side=RIGHT, fill=Y)
           lb = Listbox(v, yscrollcommand=sc.set)
           lb.pack(side=BOTTOM, fill = BOTH)
           sc.config(command = lb.yview)
           #Importante: el diccionario solo contiene los campos que han sido almacenados(stored=True) en el Schema
           for r in results:
               lb.insert(END,r["categoria"])
               lb.insert(END,r["fecha"])
               lb.insert(END,r["titulo"])
               lb.insert(END,'')
 
   v = Toplevel()
   v.title("Busqueda de noticias")
   l = Label(v, text="Seleccione la categoria:")
   l.pack(side=LEFT)
   ix=open_dir("Index")
   categorias = []
   with ix.searcher() as searcher:
       categorias = [i.decode('utf-8') for i in searcher.lexicon('categoria')]
   en = Spinbox(v,values=categorias)
   en.bind("<Return>", mostrar_lista)
   en.pack(side=LEFT)
 
def eliminar_noticia():
    def eliminar(event):
        ix=open_dir("Index")
        with ix.searcher() as searcher:
            query = QueryParser("titulo", ix.schema).parse(str(en.get()))
            results = searcher.search(query, limit=None)
 
            #Se crea una ventana con título de un tamaño prefijado
            v = Toplevel()
            v.title("Listado de Noticias a Eliminar")
            v.geometry('800x150')
            #Se crea scroll vertical en el margen derecho
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            #Se crea un espacio de listado
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            #Recorremos los resultados obtenidos(es una lista de diccionarios) y mostramos lo solicitado
            #Importante: el diccionario solo contiene los campos que han sido almacenados(stored=True) en el Schema
            for r in results:
                lb.insert(END,r['categoria'])
                lb.insert(END,r['fecha'])
                lb.insert(END,r['titulo'])
                lb.insert(END,'')
       
        # Se lanza mensaje de alerta, que si se acepta
        respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere eliminar estas noticias?")
        if respuesta:
            writer = ix.writer()
            writer.delete_by_term('titulo', str(en.get()), searcher=None)
            writer.commit()
   
    v = Toplevel()
    v.title("Eliminar Noticia")
    l = Label(v, text="Introduzca:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", eliminar)
    en.pack(side=LEFT)
 
 
def ventana_principal():
    root = Tk()
    root.geometry('300x300')
    menubar = Menu(root)
   
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar)
    datosmenu.add_separator()  
    datosmenu.add_command(label="Salir", command=root.quit)
   
    menubar.add_cascade(label="Datos", menu=datosmenu)
 
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Título", command=buscar_titulo)
    buscarmenu.add_command(label="Resumen o Título", command=buscar_titulo_resumen)
    buscarmenu.add_command(label="Fecha", command=buscar_fecha)
    buscarmenu.add_command(label="Categoría", command=buscar_categoria)
 
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
 
    datosmenu = Menu(menubar, tearoff=0)    
    menubar.add_cascade(label="Eliminar Noticias", command=eliminar_noticia)
       
    root.config(menu=menubar)
    root.mainloop()
 
if __name__ == "__main__":
    ventana_principal()

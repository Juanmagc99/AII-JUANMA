from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh import query
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID
from whoosh.qparser import QueryParser, OrGroup

# lineas para evitar error SSL
import ssl

from whoosh.qparser.default import MultifieldParser
from whoosh.searching import NoTermsException, Results
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_peliculas():

    l_peliculas = []

    f = urllib.request.urlopen('https://www.elseptimoarte.net/estrenos/')
    s = BeautifulSoup(f, 'lxml')
    lista_links = s.find('ul', attrs={'class':'elements'}).find_all('li')
    for link in lista_links:
        f = urllib.request.urlopen('https://www.elseptimoarte.net/' + link.a['href'])
        s = BeautifulSoup(f, 'lxml')
        datos = s.find('main', attrs={'class':'informativo', 'id':'content'})
        
        titulo_og = datos.find('dt', text='Título original').find_next_sibling('dd').string.strip()
        titulo = datos.find('dt',text='Título').find_next_sibling('dd').string.strip()
        if titulo == None:
            titulo = titulo_og
        
        pais = ''.join(datos.find('dt', text='País').find_next_sibling('dd').stripped_strings)
        fecha = datetime.strptime(datos.find('dt', text='Estreno en España').find_next_sibling('dd').string.strip(), '%d/%m/%Y')

        generos_directores = s.find('div', id='datos_pelicula')
        generos = "".join(generos_directores.find('p', class_='categorias').stripped_strings)
        directores = "".join(generos_directores.find('p', class_='director').stripped_strings)    

        l_peliculas.append((titulo_og, titulo, pais, fecha, generos, directores))

    return l_peliculas



def cargar_datos():

    schema = Schema(titulo_og=TEXT(stored=TRUE), titulo=TEXT(stored=TRUE), pais=TEXT(stored=TRUE), estreno=DATETIME(stored=TRUE), 
    generos=KEYWORD(stored=TRUE, commas=TRUE, lowercase=TRUE), directores=KEYWORD(stored=TRUE, commas=TRUE, lowercase=TRUE))

    '''En caso de existir el directorio de indice lo borramos y creamos de nuevo'''
    if os.path.exists('Index'):
        shutil.rmtree('Index')
    os.mkdir('Index')
    
    '''Se crea el indice dentro del directorio anterior y se habre el escritor'''
    ix = create_in('Index', schema=schema)
    writer = ix.writer()
    i = 0

    lista = extraer_peliculas()

    for p in lista:
        '''Añadimos mediante el escritor los campos correspondiente y al finalizar se hace 
        commit para asi guardar los cambios efectuados'''
        writer.add_document(titulo_og=str(p[0]), titulo=str(p[1]), pais=str(p[2]), estreno=p[3], 
        generos=str(p[4]), directores=str(p[5]))
        i += 1
    writer.commit()

    messagebox.showinfo('Fin del indexado', 'Se han indexado '+str(i)+' peliculas')

def busqueda_titulo():
    def mostrar_lista(event):
        '''Abrimos el indice para poder trabajar con el'''
        ix = open_dir('Index')
        
        with ix.searcher() as searcher:

            '''Creamos la query al ser este un caso con un solo atributo se usa queryparser'''
            query = QueryParser('titulo', ix.schema, group=OrGroup).parse(str(en.get()))
            results = searcher.search(query)
            
            v = Toplevel()
            v.title("Listado de Peliculas")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)

            for r in results:
                lb.insert(END, r['titulo_og'])
                print(r['directores'])
                lb.insert(END, r['directores'].replace('_', ' '))
                lb.insert(END, '==============================================================')

    v = Toplevel()
    v.title('Busqueda por título o por sipnosis')
    l = Label(v, text="Intuduzca palabras a buscar")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind('<Return>', mostrar_lista)
    en.pack(side=LEFT)

def busqueda_genero():
    def mostrar_lista(event):
        ix = open_dir('Index')
        with ix.searcher() as searcher:
            '''Obtenemos una lista con todos los generos posibles se usa el decode para 
            parsear de binario a utf-8'''
            l_generos = [i.decode('utf-8') for i in searcher.lexicon('generos')]
            print(l_generos)
            entrada = str(en.get().replace(' ', '_').lower())

            if entrada not in l_generos:
                messagebox.showinfo("Error", "No existe dicho genero entre las peliculas almacenadas")
                return
            
            query = QueryParser('generos', ix.schema).parse(entrada)
            results = searcher.search(query, limit=20)
            v = Toplevel()
            v.title("Listado de PelÃ­culas")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            for r in results:
                lb.insert(END,r['titulo'])
                lb.insert(END,r['titulo_og'])
                lb.insert(END,r['pais'].replace('_',' '))
                lb.insert(END,'========================================================')



    v = Toplevel()
    v.title('Busqueda por genero')
    l = Label(v, text='Introduzca un género: ')
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind('<Return>', mostrar_lista)
    en.pack(side=LEFT)
    
def buscar_fecha():
    def mostrar_lista(event):
        if not re.match('\d{8} \d{8}', en.get()):
            messagebox.showinfo("Error", "Formato del rango de fecha incorrecto")
            return
        ix = open_dir('Index')
        with ix.searcher() as searcher:
            aux = en.get().split()
            rango = '[' + aux[0] + ' TO ' + aux[1] +']'
            query = QueryParser('estreno', ix.schema).parse(rango)
            results = searcher.search(query, limit=None)

            v = Toplevel()
            v.title('Listado de peliculas')
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill=BOTH)
            sc.config(command=lb.yview)
            for r in results:
                lb.insert(END,r['titulo'])
                lb.insert(END,r['estreno'])
                lb.insert(END,'============================================================')

    v = Toplevel()
    v.title('Busqueda por fecha')
    l = Label(v, text='Introduce rango de fechas con formato AAAAMMDD AAAAMMDD:')
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind('<Return>', mostrar_lista)
    en.pack(side=LEFT)

def modificar_fecha():
    def modificar():
        if not re.match('\d{8}', en1.get()):
            messagebox.showinfo("Error", "Formato del rango de fecha incorrecto")
            return

        ix = open_dir('Index')
        lista = []
        with ix.searcher() as searcher:
            query = QueryParser('titulo', ix.schema).parse(en.get())
            res = searcher.search(query, limit=None)

            v = Toplevel()
            v.title('Lista de peliculas que modificas')
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            for r in res:
                lb.insert(END,r['titulo'])
                lb.insert(END,r['estreno'])
                lb.insert(END,'')
                lista.append(r)

        respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere modificar las fechas de estrenos de estas peliculas?")
        if respuesta:
            writer = ix.writer()
            for r in lista:
                writer.update_document(estreno=str(en1.get()), titulo=r['titulo'], titulo_og=r['titulo_og'], pais=r['pais'], directores=r['directores'], generos=r['generos'])
            writer.commit()

    v = Toplevel()
    v.title('Modifique la fecha')
    l = Label(v, text='Introduce titulo de pelicula:')
    l.pack(side=LEFT)
    en = Entry(v)
    en.pack(side=LEFT)
    l1 = Label(v, text='Introduce la nueva fecha:')
    l1.pack(side=LEFT)
    en1 = Entry(v)
    en1.pack(side=LEFT)
    bt = Button(v, text='Modificar', command=modificar)
    bt.pack(side=LEFT)


def ventana_principal():
    app = Tk()
    menu = Menu(app)

    #DATOS
    menuDatos = Menu(menu, tearoff=0)
    menuDatos.add_command(label='Carga', command=cargar_datos)
    menuDatos.add_command(label='Salir', command=app.quit)
    menu.add_cascade(label='Datos', menu=menuDatos)

    #BUSQUEDA
    menuBusqueda = Menu(menu, tearoff=0)
    menuBusqueda.add_command(label='Buscar por título', command=busqueda_titulo)
    menuBusqueda.add_command(label='Buscar por generos', command=busqueda_genero)
    menuBusqueda.add_command(label='Buscar por fecha', command=buscar_fecha)
    menuBusqueda.add_command(label='Cambiar fecha', command=modificar_fecha)
    menu.add_cascade(label='Busqueda', menu=menuBusqueda)

    app.config(menu=menu)
    app.mainloop()


if __name__ == '__main__':
    ventana_principal()
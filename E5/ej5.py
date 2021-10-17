#encoding:utf-8

from sqlite3.dbapi2 import Cursor, connect
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime
# lineas para evitar error SSL
import os, ssl


if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


#título, título original, país/es, fecha de estreno en España, director y género/s

def cargar():
    respuesta = messagebox.askyesno(title="Confimar", message="¿Estas seguro de cargar los datos?")
    if respuesta:
        almacenar_bd()


def almacenar_bd():

    ''''Creamos una conexión a la base de datos y la tabla que cargaremos'''

    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str
    conn.execute('''DROP TABLE IF EXISTS PELICULA''')
    conn.execute('''CREATE TABLE PELICULA
    (TITULO TEXT NOT NULL,
    TITULO_ORIGINAL TEXT,
    PAIS TEXT,
    FECHA DATE,
    DIRECTOR TEXT,
    GENEROS TEXT);''')

    '''Abrimos la url de la pagina que queremos obtener con urllib'''
    f = urllib.request.urlopen("https://www.elseptimoarte.net/estrenos/")

    '''Usamos Beautifulsoup con el fomarto lxml para poder navegar y pedir datos de la pagina obtenida'''
    s = BeautifulSoup(f, 'lxml')

    '''Devuelve de todas la listas ul con la clase=elements, sus li'''
    lista_link_peliculas = s.find('ul', class_='elements').find_all('li')
    
    for link_pelicula in lista_link_peliculas:
        '''De cada link busco el elemento html 'a' y obtengo su atributo href'''
        f = urllib.request.urlopen("https://www.elseptimoarte.net/"+link_pelicula.a['href'])
        s = BeautifulSoup(f, 'lxml')
        
        '''Podemos ir concatenando un find tras otro para profundizar en los elementos
        se pude usar el attr directamente o pasarle el diccionario con unos pocos atributos
        a cumplir en la busqueda'''
        #datos = s.find('main', id='content', class_='informativo').find('section', class_='highlight').find('div').find('dl')
        datos = s.find('main', attrs={'id':'content', 'class':'informativo'}).find('section', class_='highlight').find('div').find('dl')
        
        '''Next sibling nos da el siguiente elemento que comparta nodo con las características que le idiquemos'''
        titulo_og = datos.find('dt', text='Título original').find_next_sibling('dd').string.strip()
        
        '''Puede ser que no tenga titulo, así que se comprueba y en caso contrario usamos el original'''
        titulo = datos.find('dt', text='Título').find_next_sibling('dd').string.strip()
        if titulo == None:
            titulo = titulo_og

        '''Puesto que pueden ser varios paises,generos o directores, dentro de elementos html 'a' usaremos stripped_strings
        que coge directamente los textos dentro de un nodo en concreto en este caso todos los 'a' del 'dd' '''
        pais = ''.join(datos.find('dt',text='País').find_next_sibling('dd').stripped_strings)
        fecha = datetime.strptime(datos.find('dt', text='Estreno en España').find_next_sibling('dd').string.strip(), '%d/%m/%Y')

        generos_directores = s.find('div', id='datos_pelicula')
        generos = "".join(generos_directores.find('p', class_='categorias').stripped_strings)
        directores = "".join(generos_directores.find('p', class_='director').stripped_strings)

        conn.execute("""INSERT INTO PELICULA (TITULO, TITULO_ORIGINAL, PAIS, FECHA, DIRECTOR, GENEROS) VALUES (?,?,?,?,?,?);""",
        (titulo, titulo_og, pais, fecha, directores, generos))
        conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM PELICULA")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def listar():
    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT TITULO, PAIS, DIRECTOR FROM PELICULA")
    conn.close
    listar_peliculas(cursor)


def listar_peliculas(cursor):
    '''Se crea una nueva pagina con una barra de scroll a la derecha que ocupa todo el eje Y
    a continuacion se añade la lista y se van insertando las entradas de la DB en ella'''
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=180, yscrollcommand=sc.set)

    for row in cursor:
        s = 'Título: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "-----------------------------------------------------------------------")
        s = 'País: ' + str(row[1]) + ' | Diictor: ' + row[2]
        lb.insert(END, s)
        lb.insert(END, "\n\n")
    
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def buscar_por_genero():
    def listar(Event):
        conn = sqlite3.connect('peliculas.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT TITULO, PAIS, DIRECTOR FROM PELICULA where GENEROS LIKE '%" + str(entry.get())+"%'")
        conn.close
        listar_peliculas(cursor)

    '''Extreamos todos los apartados generos de la db en las entradas de cada pelicula,
    para despues pasarlo a un conjunto donde no se repita'''
    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT GENEROS FROM PELICULA")

    generos = set()
    for i in cursor:
        generos_pelicula = i[0].split(',')
        for g in generos_pelicula:
            generos.add(g.strip())

    v = Toplevel()
    entry = Spinbox(v, values=list(generos))
    entry.bind("<Return>", listar)
    entry.pack()

    conn.close()


def buscar_por_titulo():
    def listar(event):
        conn = sqlite3.connect('peliculas.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT TITULO, PAIS, DIRECTOR FROM PELICULA WHERE TITULO LIKE'%" + str(entry.get()) + "%'")
        conn.close
        listar_peliculas(cursor)

    v = Toplevel()
    entry = Entry(v)
    entry.bind("<Return>", listar)
    entry.pack()


def ventana_principal():
    app = Tk()

    menu = Menu(app)

    #Datos
    menuDatos = Menu(menu, tearoff=0)
    menuDatos.add_command(label="Cargar", command=cargar)
    menuDatos.add_command(label="Listar", command=listar)
    menuDatos.add_command(label="Salir", command=app.quit)
    menu.add_cascade(label="Datos", menu=menuDatos)

    #Buscar
    menuBuscar = Menu(menu, tearoff=0)
    menuBuscar.add_command(label="Titulo", command=buscar_por_titulo)
    menuBuscar.add_command(label="Fecha")
    menuBuscar.add_command(label="Generos", command=buscar_por_genero)
    menu.add_cascade(label="Buscar", menu=menuBuscar)

    app.config(menu=menu)

    app.mainloop()



if __name__ == "__main__":
    ventana_principal()



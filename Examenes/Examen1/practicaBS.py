#encoding:utf-8

'''Realizada por Juan Manuel García Criado
Fernando Miguel Hidelago Aguilar
Miguel Molina Rubio'''


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


def cargar_bd():

    conn = sqlite3.connect('libros.db')
    conn.text_factory = str
    conn.execute('''DROP TABLE IF EXISTS LIBRO''')
    conn.execute('''CREATE TABLE LIBRO
    (TITULO TEXT NOT NULL,
    AUTOR TEXT,
    EDITORIAL TEXT,
    ESTADO TEXT,
    PRECIO TEXT,
    LIBRERIA TEXT,
    TLF INTEGER);''')

    for j in range(0,2):
        f = urllib.request.urlopen('https://www.uniliber.com/buscar/libros_pagina_'+str(j+1)+'?descripcion%5B0%5D=CL%C3%81SICOS')
        s = BeautifulSoup(f, 'lxml')

        list_libros = s.find('div', attrs={'class':'listado_detallado'}).find_all('div', attrs={'class':'description'})
        
        for l in list_libros:
            titulo = l.find('a', class_='title').string.strip()
            print(titulo)
            
            if not l.find('div', class_='subtitle').text:
                autor=''
            else:
                autor = l.find('div', class_='subtitle').string.strip()
                print(autor)

            datos = l.find('div', class_='subtitle').find_next_siblings('div')

            editorial=''
            estado=''
            
            for i in datos:
                if 'Editorial' in i.text:
                    editorial = i.text.replace("Editorial: ",'').replace('.','')
                    print(editorial)
                if 'Estado de conservación' in i.text:
                    estado = i.text.split(': ')[1]
                    print(estado)
            
            precio = l.find('span', class_ = 'precio').text
            print(precio)
            libreria = l.find('a', class_='libreria').text
            print(libreria)
        
            f = urllib.request.urlopen('https://www.uniliber.com'+l.find('a', class_='libreria')['href'])
            s = BeautifulSoup(f, 'lxml')

            tabla = s.find('div', attrs={'class':'info-libreria'}).find('table').find_all('td')
            tlf = tabla[1].text
            print(tlf)

            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            
            
            conn.execute("""INSERT INTO LIBRO (TITULO,
        AUTOR,
        EDITORIAL,
        ESTADO,
        PRECIO,
        LIBRERIA,
        TLF) VALUES (?,?,?,?,?,?,?);""",
            (titulo, autor,editorial, estado, precio, libreria, tlf))
            conn.commit()
    
    cursor = conn.execute("SELECT COUNT(*) FROM LIBRO")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
  
    conn.close()






def ventana_principal():
    app = Tk()

    menu = Menu(app)

    #Datos
    menuDatos = Menu(menu, tearoff=0)
    menuDatos.add_command(label="Cargar", command=cargar_bd)
    menuDatos.add_command(label="Salir", command=app.quit)
    menu.add_cascade(label="Datos", menu=menuDatos)

    #Listar
    menuListar = Menu(menu, tearoff=0)
    menuListar.add_command(label="Listar Libros")
    menuListar.add_command(label="Listar Librerias")
    menu.add_cascade(label="Listar", menu=menuListar)


    #Buscar
    menuBuscar = Menu(menu, tearoff=0)
    menuBuscar.add_command(label="Por editrorial")
    menuBuscar.add_command(label="Por titulo o autor")
    menu.add_cascade(label="Buscar", menu=menuBuscar)

    app.config(menu=menu)

    app.mainloop()



if __name__ == "__main__":
    ventana_principal()
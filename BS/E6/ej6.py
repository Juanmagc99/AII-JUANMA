#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
import re

# lineas para evitar error SSL
import os, ssl


if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar_bd():

    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    conn.execute('DROP TABLE IF EXISTS VINO')
    conn.execute("""CREATE TABLE VINO (NOMBRE TEXT NOT NULL,
    PRECIO INTEGER NOT NULL,
    ORIGEN TEXT NOT NULL,
    UVAS TEXT NOT NULL);""")


    lista_vinos = []
    for i in range(0,3):
        f = urllib.request.urlopen('https://www.vinissimus.com/es/vinos/tinto/?cursor=' + str(36*i))
        s = BeautifulSoup(f, 'lxml')
        vinos = s.find_all('div', attrs={'class':'product-list-item'})
        lista_vinos.extend(vinos)
    
    for i in lista_vinos:
        nombre  = i.find('h2', attrs={'class':['title','heading']}).string.strip()
        og = i.find('div', attrs={'class':'region'}).string.strip()
        if i.find('p', attrs={'class':'dto small'}):
            precio = i.find('p', attrs={'class':'dto small'}).text
        else:
            precio = i.find('p', attrs={'class':'price'}).text
        
        print(precio)
        
    

def ventana_principal():
    app = Tk()

    menu = Menu(app)

    #Datos
    menuDatos = Menu(menu, tearoff=0)
    menuDatos.add_command(label='Cargar', command=cargar_bd)
    menu.add_cascade(label='Datos', menu=menuDatos)

    app.config(menu=menu)
    app.mainloop()

if __name__ == '__main__':
    ventana_principal()
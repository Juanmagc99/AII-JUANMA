#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_jornadas():
    f = urllib.request.urlopen("http://resultados.as.com/resultados/futbol/primera/2017_2018/calendario/")
    s = BeautifulSoup(f,"lxml")
    
    l = s.find_all("div", class_= ["cont-modulo","resultados"])
    return l


def imprimir_lista(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    jornada=0
    for row in cursor:
        if row[0] != jornada:
            jornada=row[0]
            lb.insert(END,"\n")
            s = 'JORNADA '+ str(jornada)
            lb.insert(END,s)
            lb.insert(END,"-----------------------------------------------------")
        s = "     " + row[1] +' '+ str(row[3]) +'-'+ str(row[4]) +' '+  row[2]
        lb.insert(END,s)
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)
 
def almacenar_bd():
    conn = sqlite3.connect('as.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS JORNADAS") 
    conn.execute('''CREATE TABLE JORNADAS
       (JORNADA       INTEGER NOT NULL,
       LOCAL          TEXT    NOT NULL,
       VISITANTE      TEXT    NOT NULL,
       GOLES_L        INTEGER    NOT NULL,
       GOLES_V        INTEGER NOT NULL,
       LINK           TEXT);''')
    l = extraer_jornadas()
    for i in l:
        jornada = int(re.compile('\d+').search(i['id']).group(0))
        partidos = i.find_all("tr",id=True)
        for p in partidos:
            equipos= p.find_all("span",class_="nombre-equipo")
            local = equipos[0].string.strip()
            visitante = equipos[1].string.strip()
            resultado_enlace = p.find("a",class_="resultado")
            if resultado_enlace != None:
                goles=re.compile('(\d+).*(\d+)').search(resultado_enlace.string.strip())
                goles_l=goles.group(1)
                goles_v=goles.group(2)
                link = resultado_enlace['href']
                
                conn.execute("""INSERT INTO JORNADAS VALUES (?,?,?,?,?,?)""",(jornada,local,visitante,goles_l,goles_v,link))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM JORNADAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def listar_bd():
    conn = sqlite3.connect('as.db')
    conn.text_factory = str  
    cursor = conn.execute("SELECT * FROM JORNADAS ORDER BY JORNADA")
    imprimir_lista(cursor)
    conn.close()
    

def buscar_jornada():
    def listar_busqueda(event):
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        s =  int(en.get())
        cursor = conn.execute("""SELECT * FROM JORNADAS WHERE JORNADA = ?""",(s,)) 
        imprimir_lista(cursor)       
        conn.close()
    
    v = Toplevel()
    lb = Label(v, text="Introduzca la jornada: ")
    lb.pack(side = LEFT)
    en = Entry(v)
    en.bind("<Return>", listar_busqueda)
    en.pack(side = LEFT)


def estadistica_jornada():
    def listar_estadistica(event):
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        s =  int(en.get())
        cursor = conn.execute("""SELECT SUM(GOLES_L)+SUM(GOLES_V) FROM JORNADAS WHERE JORNADA = ?""",(s,)) 
        total_goles = cursor.fetchone()[0]
        cursor = conn.execute("""SELECT GOLES_L,GOLES_V FROM JORNADAS WHERE JORNADA = ?""",(s,))
        empates=0
        locales=0
        visitantes=0
        for g in cursor:
            if g[0] == g[1]:
                empates +=1 
            elif g[0] > g[1]:
                locales +=1
            else:
                visitantes +=1          
        conn.close()
        
        s = "TOTAL GOLES JORNADA : " + str(total_goles)+ "\n\n" + "EMPATES : " + str(empates) + "\n" + "VICTORIAS LOCALES : " + str(locales) + "\n" + "VICTORIAS VISITANTES : " + str(visitantes)
        v = Toplevel()
        lb = Label(v, text=s) 
        lb.pack()
    
    v = Toplevel()
    lb = Label(v, text="Introduzca la jornada: ")
    lb.pack(side = LEFT)
    en = Entry(v)
    en.bind("<Return>", listar_estadistica)
    en.pack(side = LEFT)

   
def buscar_goles():
    def listar_busqueda():
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        cursor = conn.execute("""SELECT LINK,LOCAL,VISITANTE FROM JORNADAS WHERE JORNADA=? AND LOCAL LIKE ? AND VISITANTE LIKE ?""",(int(en_j.get()),en_l.get(),en_v.get()))
        partido = cursor.fetchone()
        enlace = "https://resultados.as.com/"+partido[0]
        conn.close()
        f = urllib.request.urlopen(enlace)
        so = BeautifulSoup(f,"lxml")
        l = so.find_all("p",class_=["txt-accion"])
        s=""
        for i in l:
            aux= i.find(class_=["hidden-xs"])
            if aux != None and aux.string == 'Gol':
                jugador = i.find('strong').string
                minuto = i.find(class_=["min-evento"]).string
                if i.find_parents("div",class_=["eventos-local"]): # el gol es del equipo local
                    s += partido[1] + "  : " + jugador + ' ' + minuto + '\n'
                else: # el gol es del equipo visitante
                    s += partido[2] + "  : " + jugador + ' ' + minuto + '\n'
                
        v = Toplevel()
        lb = Label(v, text=s) 
        lb.pack()
    
    v = Toplevel()
    lb_j = Label(v, text="Introduzca jornada: ")
    lb_j.pack(side = LEFT)
    en_j = Entry(v)
    en_j.pack(side = LEFT)
    lb_l = Label(v, text="Introduzca equipo local: ")
    lb_l.pack(side = LEFT)
    en_l = Entry(v)
    en_l.pack(side = LEFT)
    lb_v = Label(v, text="Introduzca equipo visitante: ")
    lb_v.pack(side = LEFT)
    en_v = Entry(v)
    en_v.pack(side = LEFT)
    buscar = Button(v, text="Buscar goles", command=listar_busqueda)
    buscar.pack(side=BOTTOM)


    
def ventana_principal():
    top = Tk()
    almacenar = Button(top, text="Almacenar Resultados", command = almacenar_bd)
    almacenar.pack(side = TOP)
    listar = Button(top, text="Listar Jornadas", command = listar_bd)
    listar.pack(side = TOP)
    Buscar = Button(top, text="Buscar Jornada", command = buscar_jornada)
    Buscar.pack(side = TOP)
    Buscar = Button(top, text="EstadÃ­sticas Jornada", command = estadistica_jornada)
    Buscar.pack(side = TOP)
    Buscar = Button(top, text="Buscar Goles", command = buscar_goles)
    Buscar.pack(side = TOP)
    top.mainloop()
    

if __name__ == "__main__":
    ventana_principal()


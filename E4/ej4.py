#encoding:utf-8

from sqlite3.dbapi2 import Cursor
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import re
import os, ssl


if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def almacenar_bd():
    
    conn = sqlite3.connect('as.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS JORNADA")
    conn.execute('''CREATE TABLE JORNADA
    (JORNADA INTEGER NOT NULL,
    LOCAL TEXT NOT NULL,
    VISITANTE TEXT NOT NULL,
    GOL_L INTEGER NOT NULL,
    GOL_V INTEGER NOT NULL,
    LINK TEXT);''')
    
    f = urllib.request.urlopen("https://resultados.as.com/resultados/futbol/primera/2017_2018/calendario/")
    s = BeautifulSoup(f, 'lxml')

    jornadas = s.find_all('div', attrs={'class':['cont-modulo', 'resultados']})
    
    for i in jornadas:
        n_jornada = int(re.compile('\d+').search(i['id']).group(0))
        partidos = i.find_all('tr', id=True)
        
        for p in partidos:
            equipos = p.find_all('span', attrs={'class':'nombre-equipo'})
            local = equipos[0].string.strip()
            visitante = equipos[1].string.strip()
            resultado = p.find('a', attrs={'class':'resultado'})
            if resultado != None:
                goles = re.compile('(\d+).*(\d+)').search(resultado.string.strip())
                goles_l = goles.group(1)
                goles_v = goles.group(2)
                link = resultado['href']

                conn.execute('''INSERT INTO JORNADA VALUES(?,?,?,?,?,?)'''
                ,(n_jornada, local, visitante, goles_l, goles_v, link))
    
    conn.commit()

    cursor = conn.execute('''SELECT COUNT(*) FROM JORNADA''')
    messagebox.showinfo('Se han creado ' + str(cursor.fetchone()[0]) + ' partidos en la base de datos')
    conn.close()

def listar_total():
    conn = sqlite3.connect('as.db')
    conn.text_factory = str
    cursor = conn.execute('''SELECT * FROM JORNADA''')
    conn.close
    listar_bd(cursor)

def listar_bd(cursor):
        
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=280, yscrollcommand=sc.set)

    for row in cursor:
        s = 'Jornada: ' + str(row[0])
        lb.insert(END, s)
        s = '. \n'
        s = row[1] + ' ' + str(row[3]) + ' - ' + str(row[4]) + ' ' + row[2]
        lb.insert(END, s)
        s = '++++++++++++++++++++++++++++++++++ \n\n'
        lb.insert(END, s)

    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def buscar_jornada():
    def listar(event):
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        query = "SELECT * FROM JORNADA WHERE JORNADA = ?"
        args = (int(entry.get()),)
        cursor = conn.execute(query, args)
        listar_bd(cursor)
    
    v = Toplevel()
    entry = Entry(v)
    entry.bind('<Return>', listar)
    entry.pack()
    
def estadisticas():
    def listar(event):
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        args = (int(entry.get()),)
        query = "SELECT GOL_L,GOL_V FROM JORNADA WHERE JORNADA = ?"
        cur = conn.execute(query, args)
        
        g_total = 0
        v_local = 0
        v_visitante = 0
        empates = 0

        for goles in cur:
            g_local = goles[0]
            g_visitante = goles[1]
            g_total += (g_local + g_visitante)
            
            if g_local == g_visitante:
                empates += 1
            elif g_local > g_visitante:
                v_local += 1
            else:
                v_visitante += 1
        
        v = Toplevel()
        lb = Listbox(v, width=180)

        s = 'Durante la jornada: ' + str(entry.get()) + ' se han marcado un total de ' + str(g_total) + ' goles.'      
        lb.insert(END,s)
        s = '\n'
        lb.insert(END,s)
        s = 'Empates, victorias locales, victorias visitante: ' + str(empates) + ', ' + str(v_local) + ', ' + str(v_visitante)
        lb.insert(END,s) 
        
        lb.pack(side=LEFT, fill=BOTH)


    v = Toplevel()
    entry = Entry(v)
    entry.bind('<Return>', listar)
    entry.pack()

def buscar_goles():
    def listar_busqueda():
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        cursor = conn.execute("""SELECT LINK,LOCAL,VISITANTE FROM JORNADA WHERE JORNADA=? AND LOCAL LIKE ? AND VISITANTE LIKE ?""",(int(en_j.get()),en_l.get(),en_v.get()))
        partido = cursor.fetchone()
        print(partido)
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
    
    app = Tk()

    almacenar = Button(app, text="Almacenar Resultados", command = almacenar_bd)
    almacenar.pack(side = TOP)
    
    listar = Button(app, text="Listar", command = listar_total)
    listar.pack(side=TOP)

    list_jornada = Button(app, text="Lista jornada", command = buscar_jornada)
    list_jornada.pack(side=TOP)

    list_estadistica = Button(app, text="Listar estadísticas", command = estadisticas)
    list_estadistica.pack(side=TOP)

    
    goles = Button(app, text="Listar goles", command = buscar_goles)
    goles.pack(side=TOP)

    app.mainloop()





if __name__ == '__main__':
    ventana_principal()
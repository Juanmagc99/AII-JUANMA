import tkinter
from tkinter import messagebox
import urllib.request
import sqlite3
import re

def abrir_url(url, file):
    try:
        urllib.request.urlretrieve(url, file)
        return file
    except:
        print("Fallo al conectar la url")
        return None

def extraer_datos():
    file = "noticias"
    if abrir_url("https://sevilla.abc.es/rss/feeds/Sevilla_Sevilla.xml", file):
        f = open (file, "r",encoding='utf-8')
        s = f.read()
        l1 = re.findall(r'<item>\s*<title>(.*)</title>\s*<link>(.*)</link>', s)
        l2 = re.findall(r'<pubDate>(.*)</pubDate>', s)
        l=[]
        l = [list(e1) for e1 in l1]
        for e1,e2 in zip(l,l2):
            e1.append(e2)
        f.close()
        return l[1:]

def imprimir_etiqueta(cursor):
    v = tkinter.Toplevel()
    sc = tkinter.Scrollbar(v)
    sc.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    lb = tkinter.Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(tkinter.END,row[0])
        lb.insert(tkinter.END,row[1])
        lb.insert(tkinter.END,row[2])
        lb.insert(tkinter.END,'')
    print('Hola')
    lb.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
    sc.config(command = lb.yview)

def almacenar_bd():
    conn = sqlite3.connect("noticias.db")
    conn.text_factory = str
    conn.execute('DROP TABLE IF EXISTS NOTICIAS')
    conn.execute('''CREATE TABLE NOTICIAS
       (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
       TITULO           TEXT    NOT NULL,
       LINK           TEXT    NOT NULL,
       FECHA        DATE NOT NULL);''')
    
    l = extraer_datos()
    for i in l:
        conn.execute("""INSERT INTO NOTICIAS (TITULO, LINK, FECHA) VALUES (?,?,?)""",(i[0],i[1],i[2]))
        conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM NOTICIAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()

def listar_bd():
    conn = sqlite3.connect('noticias.db')
    conn.text_factory = str  
    cursor = conn.execute("SELECT TITULO,LINK, FECHA FROM NOTICIAS")
    imprimir_etiqueta(cursor)
    conn.close()

def buscar_mes_bd():
    def listar_busqueda(event):
        conn = sqlite3.connect('noticias.db')
        conn.text_factory = str
        s = "%"+en.get()+"%" 
        print(s)
        cursor = conn.execute("SELECT TITULO,LINK,FECHA FROM NOTICIAS WHERE FECHA LIKE '%"+en.get()+"%'")
        imprimir_etiqueta(cursor)
        conn.close()
    
    v = tkinter.Toplevel()
    lb = tkinter.Label(v, text="Introduzca el mes (Xxx): ")
    lb.pack(side = tkinter.LEFT)
    en = tkinter.Entry(v)
    en.bind("<Return>", listar_busqueda)
    en.pack(side = tkinter.LEFT)



def ventana_principal():
    top = tkinter.Tk()
    buttonFrame = tkinter.Frame(top)
    buttonFrame.grid(row=1,column=4, columnspan=2)
    tkinter.Button(buttonFrame,text="Almacenar", command=almacenar_bd).grid(row=0, column=0)
    tkinter.Button(buttonFrame,text="Listar", command=listar_bd).grid(row=0, column=1)
    tkinter.Button(buttonFrame,text="Buscar mes", command=buscar_mes_bd).grid(row=0, column=2)
    tkinter.Button(buttonFrame,text="Buscar dia").grid(row=0, column=3)
    top.mainloop()


if __name__ == '__main__':
    ventana_principal()
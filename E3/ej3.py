import csv
from tkinter import *
from tkinter import messagebox
import sqlite3

def extraerDatos(fichero):
    try:
        with open(fichero) as f:
            l = [row for row in csv.reader(f, delimiter=';', quotechar='"')] 
        return l[1:] 
    except:
        messagebox.showerror("Error", "Error en la apertura del fichero de libros" )
        return None



def almacenarBD(libros):
    conn = sqlite3.connect("E3/books")
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS BOOKS")
    conn.execute('''CREATE TABLE BOOKS
    (ISBN CHAR(9) PRIMARY KEY,
    TITLE TEXT NOT NULL,
    AUTHOR TEXT NOT NULL,
    YEAR INTEGER NOT NULL,
    PUBLISHER TEXT NOT NULL);''')

    for i in libros:
        if i[2] == 'Unknown':
            i[2] = 0
        
        conn.execute("""INSERT INTO BOOKS (ISBN, TITLE, AUTHOR, YEAR, PUBLISHER)
        VALUES (?,?,?,?,?);""",(i[0],i[1],i[2],i[3],i[4]))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM BOOKS")
    messagebox.showinfo(title="Base de datos", message= "Se ha creado de manera correcta una base de datos con " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def cargarDatos():
    respuesta = messagebox.askyesno(title="Confirmar", message="¿Quiere cargar los datos?")
    if(respuesta):
        libros=extraerDatos('E3/books.csv')
        print(libros)
        if(libros):
            almacenarBD(libros)


def ventanaPrincipal():
    app = Tk()
    menuBar = Menu(app)

    #Datos
    menuDatos = Menu(menuBar, tearoff=0)
    menuDatos.add_command(label="Cargar", command=cargarDatos)
    menuDatos.add_command(label="Salir", command=app.quit)
    menuBar.add_cascade(label="Datos", menu=menuDatos)

    app.config(menu=menuBar)

    app.mainloop()



if __name__ == "__main__" :
    ventanaPrincipal()
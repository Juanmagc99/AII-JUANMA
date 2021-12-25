#encoding:utf-8
from principal.models import Temporada, Equipo, Jornada, Partido
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.conf import settings
from principal import populateDB
from django.db.models import Max


def cargar(request):
    if populateDB.populateDatabase():
        tem = Temporada.objects.all().count()
        equ = Equipo.objects.all().count()
        jor = Jornada.objects.all().count()
        par = Partido.objects.all().count()
        html="<html><body>Datos cargados correctamente\n" + "Temporadas: " + str(tem) + " ; " + "Jornadas: " + str(jor) + " ; " + "Partidos: " + str(par) + " ; " + "Equipos: " + str(equ) +"</body></htm>"
    else:
        html="<html><body>ERROR en la carga de datos</body></htm>"    
    return HttpResponse(html)

#muestra los títulos de las recetas que están registradas
def inicio(request):
    temporadas=Temporada.objects.all()
    return render(request,'inicio.html', {'temporadas':temporadas})

#muestra el nombre de los equipos almacenados (con un enlace a detalle de cada uno)
def lista_equipos(request):
    equipos=Equipo.objects.all()
    return render(request,'equipos.html', {'datos':equipos})

#muestra detalles de un equipo (nombre, fundación, estadio, aforo y dirección)
def detalle_equipo(request, id_equipo):
    equipo = get_object_or_404(Equipo, pk=id_equipo)
    return render(request,'equipo.html',{'equipo':equipo})

#muestra los cinco estadios con más aforo (nombre equipo, estadio y aforo)
def estadios_mayores(request):
    equipos = Equipo.objects.all().order_by('-aforo')[:5]
    return render(request,'estadios_mayores.html',{'equipos':equipos})

#muestra los resultados de la última temporada, agrupados por jornadas
def ultima_temporada(request):
    ultimo = Temporada.objects.all().aggregate(ultimo_anyo= Max('anyo'))
    partidos = Partido.objects.all().filter(jornada__temporada__anyo=ultimo['ultimo_anyo'])
    return render(request,'ultima_temporada.html',{'partidos':partidos , 'anyo':ultimo['ultimo_anyo']})


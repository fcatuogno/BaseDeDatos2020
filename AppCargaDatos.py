#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlobject as SO
import time
import json


def menu():
    """
    Función que limpia la pantalla y muestra nuevamente el menu
    """
    os.system('clear')
    print ('#--------------------------------------------------------------------------------#')
    print ("Modulo Cargador de datos".center(80, " "))
    print ('#--------------------------------------------------------------------------------#')
    print ('El modulo se encuentra recibiendo y cargando todos los datos correctamente'.center(80, "*"))
    print ('#--------------------------------------------------------------------------------#')
    print ('Seleccione una opcion:')
    print ("\t1 - Listar todas las lineas")
    print ("\t2 - Agregar una linea a un tablero existente")
    print ("\t3 - Agregar un tablero a un edificio existente")
    print ("\t4 - Agregar edificio")
    print ('#--------------------------------------------------------------------------------#')



class TablaPrueba(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)

    campoUno = SO.IntCol()
    campoDos = SO.StringCol(length=160, varchar=True)
    edificio = SO.ForeignKey('Edificio')

class Edificio(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)
    nombre = SO.StringCol(length=25, varchar=True)		
    direccion = SO.StringCol(length=50, varchar=True)

class Tablero(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)	
    nombre = SO.StringCol(length=25, varchar=True)		
    edificio = SO.ForeignKey('Edificio')

class Linea(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)  
    nombre = SO.StringCol(length=25, varchar=True)      
    tablero = SO.ForeignKey('Tablero')

class Unidad(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)  
    unidad = SO.StringCol(length=25, varchar=True)   

class Medicion(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)
    intervalo = SO.IntCol()
    linea = SO.ForeignKey('Linea')
    unidad = SO.ForeignKey('Unidad')

class ValorMedicion(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)

    valor = SO.DecimalCol(size=10, precision=2)
    unixTimeStamp = SO.IntCol()
    medicion = SO.ForeignKey('Medicion')

class Umbral(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)

    severidad = SO.EnumCol(enumValues=('leve', 'grave', 'critico'))
    umbralInferior = SO.DecimalCol(size=10, precision=2)
    umbralSuperior = SO.DecimalCol(size=10, precision=2) 
    unidad =SO.ForeignKey('Unidad')

class Alarma(SO.SQLObject):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)
    umbral =SO.ForeignKey('Umbral')
    valor =SO.ForeignKey('ValorMedicion')


if __name__ == "__main__":
    # declaro la conexion asi -> "mysql://user:password@host/database"
    connection = SO.connectionForURI(
        "mysql://guest:guest@localhost/AuditorRed"
    )
    SO.sqlhub.processConnection = connection
    # connection.debug = True

    TablaPrueba.dropTable(ifExists=True)
    TablaPrueba.createTable()

#    ValorMedicion(valor=220, unixTimeStamp=time.time(), Medicion = 0)
#    Edificio(nombre = 'Costanera', direccion = 'Aguero 2340')
#    Tablero(nombre = 'Motores', edificioID = 1)
#     TablaPrueba(campoUno = 28, campoDos = 'coso', edificioID = 3)

while True:
    menu()
    opcion = input()

    if opcion=="1":
        
        for edificio in Edificio.select(orderBy=Edificio.q.nombre):
            print(f'Edificio {edificio.nombre}:')
            for tablero in Tablero.select(Tablero.q.edificio == edificio):
                print(f'\tTablero {tablero.nombre}:')
                for linea in Linea.select(Linea.q.tablero == tablero):
                    print(f'\t\t {linea.nombre}')
                    #payload = getattr(linea, json.dumps(dict(linea.sqlmeta.columns)))
                    payload = linea.sqlmeta.columns
                    for a in payload:
                        print(f'\t\t\t' + a)

        input("Presione enter para volver al menu principal")
    elif opcion=="2":

        print ("Tableros listados:")
        for edificio in Edificio.select(orderBy=Edificio.q.nombre):
            print(f'Edificio {edificio.nombre} :')
            for tablero in Tablero.select(Tablero.q.edificio == edificio):
                print(f'\tID: {tablero.id} - {tablero.nombre}')

        tablero_id = input("Ingrese ID del tablero donde se encuentra la linea")
        try: 
            resultado = Tablero.get(int(tablero_id))
            nombre_ingresado=input("Ingrese Nombre de la linea: ")

            retorno = Linea(nombre = nombre_ingresado, tableroID = tablero_id)
            print(f"Se agregó {retorno}")
            
        except:
            print("Debe ingresar un ID de Tablero valido")

        input("presione enter para volver al menu principal")

    elif opcion=="3":
        print ("Edificios listados:")
        for edificio in list(Edificio.select(orderBy=Edificio.q.nombre)):
            print(edificio)           
        edificio_id = input("Ingrese N° Edificio donde cargar la linea:")     
        try: 
            resultado = Edificio.get(int(edificio_id))
            nombre_ingresado=input("Ingrese Nombre del tablero: ")

            #Verifico que no exista en la DB:
            resultado = list(Tablero.selectBy(nombre=nombre_ingresado))

            if resultado:
                print(f"Se encontraron los siguientes registros con nombre {nombre_ingresado}:")
                for entradas in resultado:
                    print(entradas)
                print(f"Desea continua con la carga del Tablero {nombre_ingresado}?")
                print("y/n")
                respuesta = input()
                if respuesta=="y":
                    retorno = Tablero(nombre = nombre_ingresado, edificioID = edificio_id)
                    print(f"Se agregó {retorno}")
                else:
                    input("Se canceló carga, presione enter para volver al menu principal")
            else:
                retorno = Tablero(nombre = nombre_ingresado, edificioID = edificio_id)
                print(f"Se agregó {retorno}")
        except:
            print("Debe ingresar un N° de edificio valido")

        input("presione enter para volver al menu principal")



    elif opcion=="4":
        print ("Ingrese nombre del edificio a agregar:")
        nombre_ingresado=input()

        #Verifico que no exista en la DB:
        resultado = list(Edificio.selectBy(nombre=nombre_ingresado))

        if resultado:
            print(f"Se encontraron los siguientes registros con nombre {nombre_ingresado}:")
            for entradas in resultado:
                print(entradas)
            print(f"Desea continua con la carga del edificio {nombre_ingresado}?")
            print("y/n")
            respuesta = input()
            if respuesta=="y":
                direccion_ingresada=input("Ingrese direccion edificio:")
                retorno = Edificio(nombre = nombre_ingresado, direccion = direccion_ingresada)
                print(f"Se agregó {retorno}")
                input("presione enter para volver al menu principal")
            else:
                input("Se canceló carga, presione enter para volver al menu principal")
        else:
            direccion_ingresada=input("Ingrese direccion edificio:")
            retorno = Edificio(nombre = nombre_ingresado, direccion = direccion_ingresada)
            print(f"Se agregó {retorno}")
            input("presione enter para volver al menu principal")

    elif opcion=="5":

        break
    else:
        print ("")
        input("No has pulsado ninguna opción correcta...\npulsa una tecla para continuar")
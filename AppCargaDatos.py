#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlobject as SO
import time
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import threading



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
    print ("\t1 - Listar todas las mediciones")
    print ("\t2 - Agregar una linea a un tablero existente")
    print ("\t3 - Agregar un tablero a un edificio existente")
    print ("\t4 - Agregar edificio")
    print ("\t5 - Agregar una medicion a una linea existente")
    print ("\t6 - Agregar una magnitud a medir")
    print ('#--------------------------------------------------------------------------------#')

#Metodos MQTT
def Listen(topic):
    subscribe.callback(on_message, topic, qos=0, userdata=None, hostname="localhost",
    port=1883, client_id="digi_mqtt_test", keepalive=60, will=None, auth=None, tls=None)


def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print("Message received-> "+ str(msg.payload))  # Print a received msgr

#Clase Serializacion de datos
class Serializer:
    def serialize(self):
        d = dict((c, getattr(self, c)) for c in self.sqlmeta.columns)
        d['id'] = self.id
        d['class'] = self.__class__.__name__
        return d

#Clases ORM
class TablaPrueba(SO.SQLObject, Serializer):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)

    campoUno = SO.IntCol()
    campoDos = SO.StringCol(length=160, varchar=True)
    edificio = SO.ForeignKey('Edificio')

class Edificio(SO.SQLObject, Serializer):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)
    nombre = SO.StringCol(length=25, varchar=True)		
    direccion = SO.StringCol(length=50, varchar=True)

class Tablero(SO.SQLObject, Serializer):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)	
    nombre = SO.StringCol(length=25, varchar=True)		
    edificio = SO.ForeignKey('Edificio')

class Linea(SO.SQLObject, Serializer):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)  
    nombre = SO.StringCol(length=25, varchar=True)      
    tablero = SO.ForeignKey('Tablero')

class Unidad(SO.SQLObject, Serializer):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)  
    unidad = SO.StringCol(length=25, varchar=True)   

class Medicion(SO.SQLObject, Serializer):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)
    nombre = SO.StringCol(length=25, varchar=True)      
    intervalo = SO.IntCol()
    linea = SO.ForeignKey('Linea')
    unidad = SO.ForeignKey('Unidad')

class ValorMedicion(SO.SQLObject, Serializer):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)

    valor = SO.DecimalCol(size=10, precision=2)
    unixTimeStamp = SO.IntCol()
    medicion = SO.ForeignKey('Medicion')

class Umbral(SO.SQLObject, Serializer):
    class sqlmeta:
        style = SO.MixedCaseStyle(longID=True)

    severidad = SO.EnumCol(enumValues=('leve', 'grave', 'critico'))
    umbralInferior = SO.DecimalCol(size=10, precision=2)
    umbralSuperior = SO.DecimalCol(size=10, precision=2) 
    unidad =SO.ForeignKey('Unidad')

class Alarma(SO.SQLObject, Serializer):
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

    #comienzo comunicacion con broker
    broker = mqtt.Client()
    broker.on_connect = on_connect  # Define callback function for successful connection
    broker.on_message = on_message  # Define callback function for receipt of a message
    broker.connect('localhost', 1883)
    broker.loop_start()

    # client = mqtt.Client("digi_mqtt_test")  # Create instance of client with client ID “digi_mqtt_test”
    # client.on_connect = on_connect  # Define callback function for successful connection
    # client.on_message = on_message  # Define callback function for receipt of a message
    # # client.connect("m2m.eclipse.org", 1883, 60)  # Connect to (broker, port, keepalive-time)
    # client.connect('localhost', 1883)

    HiloListen = threading.Thread(target=Listen, args=('AuditorRed/ValoresMedicion',), daemon = True)
    HiloListen.start()

    #Envio configuracion de mediciones a todos los modulos:
    for medicion in Medicion.select():
        d = medicion.serialize()
        payload=json.dumps(d)
        print(f'\t\t\t' + payload)
        broker.publish(topic='AuditorRed/MedicionConf', payload=payload, qos=2)
#    TablaPrueba.dropTable(ifExists=True)
#    TablaPrueba.createTable()

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
                    for medicion in Medicion.select(Medicion.q.linea==linea):
                            print(f'\t\t\tMedicion {medicion.unidad.unidad} - cada {medicion.intervalo} segundos')                           
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
        edificio_id = input("Ingrese N° Edificio donde cargar el tablero:")     
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
        print ("Lineas registradas")
        for edificio in Edificio.select(orderBy=Edificio.q.nombre):
            print(f'Edificio {edificio.nombre}:')
            for tablero in Tablero.select(Tablero.q.edificio == edificio):
                print(f'\tTablero {tablero.nombre}:')
                for linea in Linea.select(Linea.q.tablero == tablero):
                    print(f'\t\t (ID {linea.id}) - {linea.nombre}')
        lineaID = input("Ingrese ID de la linea que desea registrar mediciones:")
        resultado = list(linea.selectBy(id=lineaID))

        if resultado:
            print ("Seleccione magnitud que desea registrar mediciones:")
            for unidad in list(Unidad.select(orderBy=Unidad.q.id)):
                print(unidad.unidad)           
            magnitud=input("Magnitud a registrar: ")
            try:
                resultado = (Unidad.selectBy(unidad=magnitud).getOne())
                nombre_ingresado = input("Ingrese nombre para identificar [25 caracter MAX]")

                try:
                    retorno = Medicion(intervalo= int(intervalo), linea= lineaID, unidad = resultado.id, nombre = nombre_ingresado)
                    print(f"Se agregó {retorno}")

                    d = retorno.serialize()
                    payload=json.dumps(d)
                    print(f'\t\t\t' + payload)
                    broker.publish(topic='AuditorRed/MedicionConf', payload=payload, qos=2)
                except:
                    print(f"El nombre ingresado supera la cantidad de caracteres: {len(nombre_ingresado)}, ;Maximo: 25 caracteres")                
            except:
                print(f"{magnitud} no es magnitud válida")             
            finally:
                input("presione enter para volver al menu principal")
        else:
            print(f"El ID de linea ingresado no es válido")
            input("presione enter para volver al menu principal")
    elif opcion=="6":
        print("Magnitudes registradas")
        for unidad in list(Unidad.select(orderBy=Unidad.q.id)):
            print(unidad)           
        nombre_ingresado=input("Ingrese magnitud que desea registrar:")
        resultado = list(Unidad.selectBy(unidad=nombre_ingresado))

        if resultado:
            print(f"{nombre_ingresado} Ya se encuentra regitrado:")
            for entradas in resultado:
                print(entradas)
        else: 
            retorno = Unidad(unidad = nombre_ingresado)
            print(f"Se agregó {retorno}")
        input("presione enter para volver al menu principal")

    elif opcion=="7":
        #Salgo del programa
        break        
    else:
        print ("")
        input("No has pulsado ninguna opción correcta...\npulsa una tecla para continuar")
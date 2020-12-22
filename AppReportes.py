#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import MySQLdb
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime

class AuditorRed:
    '''
        implementa un ABM sencillo para la tabla Artist de Chinook
    '''
    def __init__(self, host, user, passwd, dbase):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._dbase = dbase
        self._conn = None

    def conectar(self):
        '''
            realiza la conexion a la base de datos
            retorna True si la conexion fue exitosa
        '''
        try:
            self._conn = MySQLdb.connect(host=self._host,
                                         user=self._user,
                                         passwd=self._passwd,
                                         db=self._dbase)
            self._conn.autocommit(True)
            return True
        except:
            print(sys.exc_info()[1])
            return False

    def _verifica_conexion(self):
        '''
            verifica que se haya realizado una conexion a la base de datos
            retorna True si ya se realizo la conexion
        '''
        if not self._conn:
            print("Error. Todavia no se ha conectado a la base de datos {}".format(self._dbase))
            return False
        return True

    def Listar_mediciones(self, edificio='%', tablero='%', linea='%'):
        if edificio is None:
                edificio = '%'
        if tablero is None:
                tablero = '%'
        if linea is None:
                linea = '%'
        curEdif = self._conn.cursor()
        curEdif.execute('SELECT * FROM Edificio WHERE Nombre LIKE %s',(edificio,))
        Edificios = curEdif.fetchall()
        curEdif.close()
        for EdificioID, Nombre, Direccion in Edificios: 
            print("Edificio {} - [{}]\t".format(Nombre, Direccion ))
            curTablero = self._conn.cursor()
            curTablero.execute('SELECT Nombre, TableroID FROM Tablero WHERE Tablero.EdificioID = %s AND Tablero.Nombre LIKE %s',(EdificioID,tablero))
            tableros = curTablero.fetchall()
            curTablero.close()
            for Nombre, TableroID in tableros:
                print("\tTablero {}".format(Nombre))
                cur = self._conn.cursor()
                cur.execute('SELECT Nombre, LineaID FROM Linea WHERE Linea.TableroID = %s AND Linea.Nombre LIKE %s',(TableroID,linea))
                lineas =  cur.fetchall()
                cur.close()
                for Nombre, LineaID in lineas:
                    print('\t\tLinea {}'.format(Nombre))
                    cur = self._conn.cursor()
                    cur.execute('''SELECT Medicion.MedicionID, Medicion.Nombre, Unidad.Unidad FROM Medicion
                        JOIN Unidad ON (Medicion.UnidadID = Unidad.UnidadID)
                        WHERE Medicion.LineaID = %s''',(LineaID,))
                    lineas =  cur.fetchall()
                    cur.close()
                    for ID, Nombre, Unidad in lineas:
                        print('\t\t\t(ID {}) - {} [{}]'.format(ID, Nombre, Unidad))
            


    def Listar_alarmas(self, severidad = '%'):
        if (severidad is None):
            severidad = '%'        

        if not self._verifica_conexion():
            return False
        try:
            cur = self._conn.cursor()
            cur.execute('''SELECT Medicion.Nombre AS 'Medicion', ValorMedicion.Valor, Unidad.Unidad, Umbral.Severidad, ValorMedicion.UnixTimeStamp 
                    FROM Alarma LEFT JOIN ValorMedicion ON (Alarma.ValorMedicionID = ValorMedicion.ValorMedicionID)
                    JOIN Umbral ON (Alarma.UmbralID = Umbral.UmbralID)
                    JOIN Medicion ON (ValorMedicion.MedicionID = Medicion.MedicionID)
                    JOIN Unidad ON (Medicion.UnidadID = Unidad.UnidadID)
                    WHERE Umbral.Severidad LIKE %s
                ''',(severidad, ))

            print("{}\t\t\t{}\t{}\t{}\t{}".format('Medicion', 'Valor','Unidad', 'Severidad', 'Fecha-Hora'))
            for Medicion, Valor, Unidad, Severidad, UnixTimeStamp in cur.fetchall():
                print("{}\t{}\t{}\t{}\t{}".format(Medicion, Valor, Unidad, Severidad, datetime.fromtimestamp(UnixTimeStamp)))
            ret = True
        except:
            print(sys.exc_info()[1])
            ret = False
        finally:
            cur.close()
        return ret


    def Graficar_medicion(self, medicionid, since=0, until=time.time()):
        colors={'leve':'tab:olive', 'grave':'orange', 'critico':'red'}
        valores = []
        diahora = []
        alarmas = []
        diahoraA = []

        if(since == None):
            since = 0;
        if(until == None):
            until=time.time()

        plt.figure()
        ret =True
        try:
            cur = self._conn.cursor()
            cur.execute(''' SELECT ValorMedicion.Valor, ValorMedicion.UnixTimeStamp, Alarma.ValorMedicionID, Umbral.Severidad
                        FROM ValorMedicion JOIN Medicion ON (ValorMedicion.MedicionID = Medicion.MedicionID)
                        LEFT JOIN Alarma ON (ValorMedicion.ValorMedicionID = Alarma.ValorMedicionID)
                        LEFT JOIN Umbral ON (Alarma.UmbralID = Umbral.UmbralID)
                        WHERE Medicion.MedicionID = %s
                        AND ValorMedicion.UnixTimeStamp BETWEEN %s AND %s
                        ORDER BY ValorMedicion.UnixTimeStamp;
                        ''', (medicionid, since, until))

            for Valor, UnixTimeStamp, Alarma, Severidad in cur.fetchall():
                valores.append(Valor)
                diahora.append(datetime.fromtimestamp(UnixTimeStamp))
                if Alarma:
                    plt.plot(datetime.fromtimestamp(UnixTimeStamp),Valor,'x',color = colors[Severidad])
            plt.plot(diahora,valores)
            plt.tick_params(axis='x', rotation=70)
        except:
            print(sys.exc_info()[1])
            ret = False
        finally:
            cur.close()

        try:
            cur=self._conn.cursor()
            cur.execute('''SELECT Medicion.Nombre, Unidad.Unidad, Umbral.UmbralSuperior, Umbral.UmbralInferior, Umbral.Severidad
                            FROM Medicion JOIN Unidad ON (Medicion.UnidadID = Unidad.UnidadID)
                            LEFT JOIN Umbral ON (Umbral.MedicionID = Medicion.MedicionID)
                            WHERE Medicion.MedicionID = %s
                        ''',(medicionid,))

            referencias=cur.fetchall()

            for nombre, unidad, umbral_inf, umbral_sup, severidad in referencias:
                if(umbral_inf):
                    plt.axhline(umbral_inf, ls='--', c=colors[severidad])
                if(umbral_sup):
                    plt.axhline(umbral_sup, ls='--', c=colors[severidad])
            #plt.legend()
            plt.title(nombre)
            plt.ylabel(unidad)
        except:
            print(sys.exc_info()[1])
            ret = False
        finally:
            cur.close()
            plt.show()
            return ret

    def Reporte(self,edificio='%', tablero='%', linea='%'):
        if edificio is None:
            edificio = '%'
        if tablero is None:
            tablero = '%'
        if linea is None:
            linea = '%'
        try:
            cur = self._conn.cursor()
            cur.execute('''SELECT Edificio.Nombre AS 'Edificio',
                            Tablero.Nombre AS 'Tablero',
                            Linea.Nombre AS 'Linea',
                            Medicion.Nombre AS 'Medicion',
                            COUNT(DISTINCT ValorMedicion.ValorMedicionID) AS 'Muestras',
                            COUNT(DISTINCT Alarma.AlarmaID) AS 'Alarmas',
                            COUNT(DISTINCT Umbral.UmbralID) AS 'Umbrales',
                            MIN(ValorMedicion.UnixTimeStamp),
                            MAX(ValorMedicion.UnixTimeStamp)
                            FROM Edificio
                            JOIN Tablero ON (Tablero.EdificioID = Edificio.EdificioID)
                            JOIN Linea ON (Linea.TableroID = Tablero.TableroID) 
                            JOIN Medicion ON (Medicion.LineaID = Linea.LineaID) 
                            LEFT JOIN Umbral ON (Medicion.MedicionID = Umbral.MedicionID)
                            JOIN ValorMedicion ON (ValorMedicion.MedicionID = Medicion.MedicionID)
                            LEFT JOIN Alarma ON (ValorMedicion.ValorMedicionID = Alarma.ValorMedicionID)
                            WHERE Edificio.Nombre LIKE %s
                            AND Tablero.Nombre LIKE %s
                            AND Linea.Nombre LIKE %s
                            GROUP BY Medicion.MedicionID
                            ''',(edificio,tablero,linea))

            print("{}\t{}\t\t{}\t\t\t{}\t\t\t\t{}\t{}\t{}\t{}\t{}".format('Edificio', 'Tablero','Linea','Medicion','Muestras', 'Alarmas','Umbrales', 'Muestra más antigua', 'Muestra más reciente'))
            for Edificio, Tablero, Linea, Medicion, Muestras, Alarmas, Umbrales, Oldest, Newest in cur.fetchall():
                print("{}\t\t{}\t{}\t{}\t\t{}\t\t{}\t{}\t\t{}\t{}".format(Edificio, Tablero, Linea, Medicion, Muestras, Alarmas,Umbrales, datetime.fromtimestamp(Oldest), datetime.fromtimestamp(Newest)))
        except:
            print(sys.exc_info()[1])
        finally:
            cur.close()



if __name__ == '__main__':

    mpl.use('TkAgg')

    auditor = AuditorRed(host='localhost',
                         user='guest',
                         passwd='guest',
                         dbase='AuditorRed')

    try:
        auditor.conectar()
    except:
        print('No pudo conectarse a la base de datos:')
        print(sys.exc_info()[1])
        exit()


    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--edificio','-e',dest='edificio')
    parent_parser.add_argument('--tablero','-t',dest='tablero')
    parent_parser.add_argument('--linea','-l',dest='linea')

    time_parser = argparse.ArgumentParser(add_help=False)
    time_parser.add_argument('--since', '-s', metavar='dd/mm/yyyy-hh:mm:ss',dest='since',help='Date Time desde cuando tomar valores')  
    time_parser.add_argument('--until', '-u', metavar='dd/mm/yyyy-hh:mm:ss',dest='until',help='Date Time hasta cuando tomar valores')

    parser = argparse.ArgumentParser(description='Realiza consultas, ejecuta reportes sobre el auditor de la red')
    #parser.add_argument('opcion', metavar='Opcion',
    #                    help='Que acción desea ejecutar del Auditor de la Red')

    subparsers = parser.add_subparsers(help='additional help', dest='opcion')

    parser_grafica = subparsers.add_parser('grafica', help='Grafica los valores de la medicion especificada mediante ID',
                                                parents=[time_parser])
    parser_grafica.add_argument('MedicionID',metavar='ID', type=int,
                             help="ID de la Medicion a graficar, consultar IDs con cmd 'medicion'")
    #parser_grafica.set_defaults(fun=auditor.Graficar_medicion(MedicionID))

    parser_mediciones = subparsers.add_parser('mediciones', help='Lista todas las mediciones configuradas',
                                                parents=[parent_parser])

    parser_alarmas = subparsers.add_parser('alarmas', help='Lista todas los valores alarmados registrados')
    parser_alarmas.add_argument('--severidad','-sev',dest='severidad', choices=['leve','grave','critico'])

    parser_reporte = subparsers.add_parser('reporte', help='Reporte de los datos registrados',
                                             parents=[parent_parser,time_parser])

  
    args= parser.parse_args()
    print(args)

    if(args.opcion == 'grafica'):

        if(args.since is not None):
            desde = datetime.strptime(args.since, "%d/%m/%Y-%H:%M:%S")
            desde = desde.timestamp()
        else:
            desde = args.since
        if(args.until is not None):
            hasta = datetime.strptime(auditorrgs.until, "%d/%m/%Y-%H:%M:%S")
            hasta = hasta.timestamp()
        else:
            hasta = args.until
        print(desde)

        auditor.Graficar_medicion(medicionid=args.MedicionID, since=desde, until=hasta)

    elif(args.opcion == 'alarmas'):
        auditor.Listar_alarmas(severidad = args.severidad)

    elif(args.opcion == 'mediciones'):
        auditor.Listar_mediciones(edificio=args.edificio, tablero=args.tablero, linea=args.linea)

    elif(args.opcion == 'reporte'):
        auditor.Reporte(edificio=args.edificio, tablero=args.tablero, linea=args.linea)
    #auditor.Listar_mediciones()
    #auditor.Reporte()


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
import MySQLdb
import matplotlib as mpl
import matplotlib.pyplot as plt

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
                print("{}\t{}\t{}\t{}\t{}".format(Medicion, Valor, Unidad, Severidad, datetime.datetime.fromtimestamp(UnixTimeStamp)))
            ret = True
        except:
            print(sys.exc_info()[1])
            ret = False
        finally:
            cur.close()
        return ret


    def Graficar_medicion(self, medicionid): #Agregar Fechas
        colors={'leve':'tab:olive', 'grave':'orange', 'critico':'red'}
        valores = []
        diahora = []
        alarmas = []
        diahoraA = []
        plt.figure()
        ret =True
        try:
            cur = self._conn.cursor()
            cur.execute(''' SELECT ValorMedicion.Valor, ValorMedicion.UnixTimeStamp, Alarma.ValorMedicionID, Umbral.Severidad
                        FROM ValorMedicion JOIN Medicion ON (ValorMedicion.MedicionID = Medicion.MedicionID)
                        LEFT JOIN Alarma ON (ValorMedicion.ValorMedicionID = Alarma.ValorMedicionID)
                        LEFT JOIN Umbral ON (Alarma.UmbralID = Umbral.UmbralID)
                        WHERE Medicion.MedicionID = %s
                        ORDER BY ValorMedicion.UnixTimeStamp;
                        ''', (medicionid,))

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
                            JOIN Umbral ON (Umbral.MedicionID = Medicion.MedicionID)
                            WHERE Medicion.MedicionID = %s
                        ''',(medicionid,))

            referencias=cur.fetchall()

            for nombre, unidad, umbral_inf, umbral_sup, severidad in referencias:
                plt.axhline(umbral_inf, ls='--', c=colors[severidad])
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

    def Reporte(self,Edificio='%', Tablero='%', Linea='%'):
        try:
            cur = self._conn.cursor()
            cur.execute('''SELECT Edificio.Nombre AS 'Edificio',
                            Tablero.Nombre AS 'Tablero',
                            Linea.Nombre AS 'Linea',
                            COUNT(ValorMedicion.MedicionID) AS 'Muestras',
                            COUNT(Alarma.ValorMedicionID) AS 'Alarmas',
                            MIN(ValorMedicion.UnixTimeStamp),
                            MAX(ValorMedicion.UnixTimeStamp)
                            FROM Edificio
                            JOIN Tablero ON (Tablero.EdificioID = Edificio.EdificioID)
                            JOIN Linea ON (Linea.TableroID = Tablero.TableroID) 
                            JOIN Medicion ON (Medicion.LineaID = Linea.LineaID) 
                            JOIN ValorMedicion ON (ValorMedicion.MedicionID = Medicion.MedicionID)
                            LEFT JOIN Alarma ON (Alarma.ValorMedicionID = ValorMedicion.ValorMedicionID)
                            WHERE Edificio.Nombre LIKE %s
                            AND Tablero.Nombre LIKE %s
                            AND Linea.Nombre LIKE %s
                            GROUP BY Medicion.LineaId;
                        ''',(Edificio,Tablero,Linea))

            print("{}\t{}\t\t{}\t\t\t{}\t{}\t\t{}\t{}".format('Edificio', 'Tablero','Linea', 'Muestras', 'Alarmas', 'Muestra más antigua', 'Muestra más reciente'))
            for Edificio, Tablero, Linea, Muestras, Alarmas, Oldest, Newest in cur.fetchall():
                print("{}\t\t{}\t{}\t{}\t\t{}\t\t{}\t{}".format(Edificio, Tablero, Linea, Muestras, Alarmas, datetime.fromtimestamp(Oldest), datetime.fromtimestamp(Newest)))
        except:
            print('Se chotió')
        finally:
            cur.close()



if __name__ == '__main__':

    mpl.use('TkAgg')

    auditor = AuditorRed(host='localhost',
                                 user='guest',
                                 passwd='guest',
                                 dbase='AuditorRed')

    auditor.conectar()

    #auditor.Listar_alarmas()
    #auditor.Listar_mediciones()
    #auditor.Graficar_medicion(medicionid = 1)
    auditor.Reporte(Edificio='coso')


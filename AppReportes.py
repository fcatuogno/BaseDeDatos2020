#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import MySQLdb

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

    def Listar_mediciones(self):
        curEdif = self._conn.cursor()
        curEdif.execute('SELECT * FROM Edificio')
        for EdificioID, Nombre, Direccion in curEdif.fetchall():
            print("{} - [{}]\t".format(Nombre, Direccion ))
            curTablero = self._conn.cursor()
            curTablero.execute('SELECT Nombre FROM Tablero WHERE Tablero.EdificioID = EdificioID')
            for Nombre in curTablero.fetchall():
                print("\t{}".format(Nombre))



    def Listar_alarmas(self, severidad = '%'):
        if not self._verifica_conexion():
            return False
        error = False
        try:
            cur = self._conn.cursor()
            cur.execute('''SELECT Medicion.Nombre AS 'Medicion', ValorMedicion.valor, Unidad.Unidad, Umbral.Severidad 
                    FROM Alarma LEFT JOIN ValorMedicion ON (Alarma.ValorMedicionID = ValorMedicion.ValorMedicionID)
                    JOIN Umbral ON (Alarma.UmbralID = Umbral.UmbralID)
                    JOIN Medicion ON (ValorMedicion.MedicionID = Medicion.MedicionID)
                    JOIN Unidad ON (Medicion.UnidadID = Unidad.UnidadID)
                    WHERE Umbral.Severidad LIKE %s;
                ''',(severidad, ))

            print("{}\t\t\t{}\t{}\t{}".format('Medicion', 'Valor','Unidad', 'Severidad'))
            for Medicion, Valor, Unidad, Severidad in cur.fetchall():
                print("{}\t{}\t{}\t{}".format(Medicion, Valor, Unidad, Severidad))
        except:
            print(sys.exc_info()[1])
            error = True
        finally:
            cur.close()
        return error

if __name__ == '__main__':

    auditor = AuditorRed(host='localhost',
                                 user='guest',
                                 passwd='guest',
                                 dbase='AuditorRed')

    auditor.conectar()

    auditor.Listar_mediciones()


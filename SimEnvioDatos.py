#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time as time
import numpy as np
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import json
import threading

LINEA = 1 #HORNOS - LUMINARIAS - LUMINARIAS 1° PISO
__MEDICION_TENSION__ = 1
__MEDICION_CORRIENTE__ = 2
__MEDICION_ID__ = 1
config_actual={}

def Listen(topic):
    print('Entro a Listen')
    subscribe.callback(on_message, topic, qos=0, userdata=None, hostname="localhost",
    port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None)

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("AuditorRed/MedicionConf")  # Subscribe to the topic “digitest/test1”, receive any messages published on it

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    
    print('cos')
    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    
    data = json.loads(msg.payload)

    if data['lineaID']==LINEA:
        if data['unidadID']==__MEDICION_TENSION__:
            periodo_tension = data['intervalo']
            print(f"Periodo nuevo Tension = {data['intervalo']}")
        elif data['unidadID']==__MEDICION_CORRIENTE__:
            periodo_tension = data['intervalo']
            print(f"Periodo nuevo Tension = {data['intervalo']}")
            config_actual = data;
        else:
            print(f"Es necesario configurar medicion = {data}")

periodo_tension = 5 #Segundos
perioso_corriente = 5 #segundos

client = mqtt.Client("digi_mqtt_test")  # Create instance of client with client ID “digi_mqtt_test”
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
# client.connect("m2m.eclipse.org", 1883, 60)  # Connect to (broker, port, keepalive-time)
client.connect('localhost', 1883)

HiloListen = threading.Thread(target=Listen, args=('AuditorRed/MedicionConf',), daemon = True)
HiloListen.start()

while True:
    tension = np.random.normal(220,220*0.05)
    TOD = time.time()

    if(config_actual):
        coso = config_actual['id']
    else:
        coso = __MEDICION_ID__
    payload=dict(valor=tension, unixTimeStamp=TOD, medicionID=coso)

    publish.single( topic='AuditorRed/ValoresMedicion',
                    payload=json.dumps(payload),
                    qos=2,
                    hostname="localhost",
                    #hostname="mqtt.eclipse.org",
                    port=1883)

    time.sleep(periodo_tension)
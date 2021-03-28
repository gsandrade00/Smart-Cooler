import paho.mqtt.client as mqtt #import the client1
import time
from datetime import datetime
import json
import os
import RPi.GPIO as GPIO


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


broker = "mqtt.mqtzao.com"
broker_port = 1883
timeout_reconnect = 60
device_id_ = '00000000ef61f377'

porta = 23
GPIO.setup(porta, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

client = mqtt.Client()
client.connect(broker, broker_port, timeout_reconnect)

client.loop_start()



from w1thermsensor import W1ThermSensor
sensor = W1ThermSensor()

while True:
    val_door = GPIO.input(porta)

    temperature = sensor.get_temperature()
    print("The temperature is %s celsius" % temperature)

    topic = 'device/temperature/'+ str(device_id_)
    out_ = {"value":str(temperature), "status_door":str(val_door)}


    data_out = json.dumps(out_)
    client.publish(topic, data_out, qos=2, retain=True)

    time.sleep(1)

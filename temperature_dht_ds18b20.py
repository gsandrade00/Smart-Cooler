import paho.mqtt.client as mqtt #import the client1
import time
from datetime import datetime
import json
import os
import Adafruit_DHT



DHT_SENSOR = Adafruit_DHT.DHT22

DHT_PIN = 26


broker = "mqtt.mqtzao.com"
broker_port = 1883
timeout_reconnect = 60
device_id_ = '00000000ef61f377'

client = mqtt.Client()
client.connect(broker, broker_port, timeout_reconnect)

client.loop_start()



from w1thermsensor import W1ThermSensor
sensor = W1ThermSensor()

while True:

    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    temperature_ds18b20 = sensor.get_temperature()

    if humidity is not None and temperature is not None:
#        print("The temperature ds18b20 is %s celsius" % temperature_ds18b20)
#        temperature = float(temperature)
#        print("DHT TEMPERATURE"  temperature)
 #       print("DHT UMIDADE" % str(humidity))

        topic = 'device/temperatura/'+ str(device_id_)
        out_ = {"value_ds18b20":str(temperature_ds18b20), "dht_temp":str(temperature), "dht_humid":str(humidity)} 


        data_out = json.dumps(out_)
        client.publish(topic, data_out, qos=2, retain=True)

        time.sleep(1)

    else:
        print("Falha ao receber os dados do sensor de umidade")

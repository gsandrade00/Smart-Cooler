import time
import sys
import paho.mqtt.client as mqtt
import paho.mqtt.client as mqtt_back
import paho.mqtt.client as mqtt_photo
import paho.mqtt.client as mqtt_start
import math
import json
import datetime
import os
import RPi.GPIO as GPIO

rele = 18
porta = 23

GPIO.setwarnings(False) # Ignore warning for now
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setmode(GPIO.BCM)

GPIO.setup(porta, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(rele, GPIO.OUT)

payload = ""
payload_button = ""
payload_photo = ""
payload_start = ""

customer_id = ""
init_picture = True
pres_picture = True
#Supervisor broker
broker = "mqtt.mqtzao.com"
broker_port = 1883
timeout_reconnect = 60

wait_time = 30

client = mqtt.Client('back')
client.connect(broker, broker_port, timeout_reconnect)
client.loop_start()

client_start = mqtt_start.Client()
client_start.connect(broker, broker_port, timeout_reconnect)
client_start.loop_start()

client_photo = mqtt_photo.Client()
client_photo.connect(broker, broker_port, timeout_reconnect)
client_photo.loop_start()

client_button = mqtt_back.Client()
client_button.connect(broker, broker_port, timeout_reconnect)

total_scope = 1

client_button.loop_start()

device_id_ = '00000000ef61f377'

def on_message(client, userdata, msg):
  global payload
  payload = json.loads(msg.payload)

def on_message_button(client, userdata, msg):
  global payload_button
  payload_button = json.loads(msg.payload)

def on_message_photo(client, userdata, msg):
  global payload_photo
  payload_photo = json.loads(msg.payload)

def on_message_start(client, userdata, msg):
  global payload_start
  payload_start = json.loads(msg.payload)

client_button.on_message = on_message_button
client_photo.on_message = on_message_photo
client_start.on_message = on_message_start

def takePicture(customer, event):
  event_name = ''
  if(event == 1):
    event_name = 'INI'  #Initialize transaction
  if(event == 2):
    event_name = 'PBT'  #Press button
  if(event == 3):
    event_name = 'SHP'  #Shop
  if(event == 4):
    event_name = 'END'  #Close door and end transaction

  #name = str(customer) + event_name + '.jpg'
  broker_out  = {"event":str(event), "customer_id": str(customer_id), "status":"on", "maintenance":"false"}
  data_out  = json.dumps(broker_out)
  client_photo.publish("supervisor/photo/" + device_id_, data_out, qos=2, retain=True)
  time.sleep(0.1)
  broker_out  = {"event":str(event), "customer_id": str(customer_id), "status":"off", "maintenance":"false"}
  data_out  = json.dumps(broker_out)
  client_photo.publish("supervisor/photo/" + device_id_, data_out, qos=2, retain=True)

  #cmd = 'fswebcam -r 1280x720 --no-banner /home/baby/images/' + name
  #os.system(cmd)
  #cmd = ''
  #name = ''

def getStatusDoor():
  try:
    status_count = 0
    for i in range(total_scope): #mudar para 8
      topic_button = "back/button/" + device_id_ + str(i + 1)
      time.sleep(0.1)
      client_button.subscribe(topic_button, 2)
      door_status = json.loads(json.dumps(payload_button))['status']
      print('aqui')
      if(door_status == "opened"):
        status_count = status_count + 1
      global payload_button
      payload_button = ''
      topic_button = ''
      door_status = ''
    time.sleep(0.1)
    return status_count
  except:
    return -1

def getStatusDoorClosed():
  try:
    status_count = 0
    for i in range(total_scope): #mudar para 8
      topic_button = "back/button/" + device_id_ + str(i + 1)
      time.sleep(0.1)
      client_button.subscribe(topic_button, 2)
      door_status = json.loads(json.dumps(payload_button))['status']
      if(door_status == "closed"):
        status_count = status_count + 1
      global payload_button
      payload_button = ''
      topic_button = ''
      door_status = ''
    time.sleep(0.1)
    return status_count
  except:
    return -1


def startScale():
  broker_out  = {"scale":"true", "back":"false", "front":"false"}
  data_out  = json.dumps(broker_out)
  client_start.publish("supervisor/initialize/" + device_id_ , data_out, qos=2, retain=True)

startScale()

GPIO.output(rele, GPIO.HIGH)

wait_val = 0

while True:
  try:
    val_door = 0
    val_door = GPIO.input(porta)
    #global customer_id
    if(len(customer_id) >= 17):
      #customer_id = raw_input('Wait for scan')
      customer_id = customer_id.rstrip()
      customer_id = customer_id.replace("\n","")
      customer_id = customer_id.replace("\r","")
      customer_id = customer_id.replace(" ","")

      broker_out  = {"light":"on", "customer_id": str(customer_id)}
      data_out  = json.dumps(broker_out)
      client.publish("back/button/event/" + device_id_ , data_out, qos=2, retain=True)
      #client.publish(str(customer_id) + "/event", data_out, qos=2, retain=True)
      #print('--------------------------------------')
      wait_val = wait_val + 1
      #print(wait_val)

      if(init_picture == True):
        takePicture(customer_id, 1)
        GPIO.output(rele, GPIO.LOW)
        global init_picture
        init_picture = False
        time.sleep(1)

      #client.subscrible('back/button/event', 2)
      #status = json.loads(json.dumps(payload_button))['status']
      #time.sleep(0.1)
      val_door = GPIO.input(porta) #getStatusDoor()

      print("status: ", val_door)

      if(val_door == 1 and wait_val >= wait_time):
        customer_id = ''
        GPIO.output(rele, GPIO.HIGH)
        wait_val = 0


      if(val_door == 0 and pres_picture == True):
        takePicture(customer_id, 2)
        global pres_picture
        pres_picture = False
        time.sleep(1)

      #end Transaction
      val_door_closed = getStatusDoorClosed()
      print("================ door_close", val_door_closed)
      print("================ press", pres_picture)
      print("================ val_door", val_door)

      if(pres_picture == False and val_door_closed < total_scope): #Espera totaol de shelfs, testar menor que total fechado
        takePicture(customer_id, 4)
        time.sleep(1)

      if(pres_picture == False and val_door == 1):
        global customer_id
        GPIO.output(rele, GPIO.HIGH)
        time.sleep(7)
        customer_id = ''

      data_out = ''
    else:
      global customer_id
      global init_picture
      init_picture = True
      global pres_picture
      pres_picture = True
      print("***********************************************************************************")
      print("***********************************************************************************")
      broker_out  = {"light":"off", "customer_id":""}
      data_out  = json.dumps(broker_out)
      client.publish("back/button/event/" + device_id_ , data_out, qos=2, retain=True)
      GPIO.output(rele, GPIO.HIGH)
      customer_id = raw_input('Wait for scan')

    time.sleep(0.1)

  except (KeyboardInterrupt, SystemExit):
    cleanAndExit()

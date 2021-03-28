import urllib, json
import RPi.GPIO as GPIO
from hx711 import HX711
import time
import sys
import paho.mqtt.client as mqtt
import paho.mqtt.client as mqtt_
import paho.mqtt.client as mqtt_back
import paho.mqtt.client as mqtt_cal
import paho.mqtt.client as mqtt_id
import paho.mqtt.client as mqtt_start
import math
import json
import datetime
from hashlib import md5
import os

EMULATE_HX711=False

referenceUnit = 10

global total_shelves
total_shelves = 0

customer_id = ""
status_port_ = 0
purchase_status_ = 0
shelves_count = 0

shelf_port = []
shelf_weigth = []
shelf_product = []
shelf_position = []
shelf_product_name = []
shelf_ean = []
shelf_id = []
shelf_device_id = []
shelf_store_id = []
shelf_store_cod = []
shelf_w_factor = []
shelf_v_factor = []
mqtt_total = []
weight_ = []
direction = []
value = []
door_status = []
shelf_weight_ = 0
reconnect_mode = False
hx = []
z = 0
payload_update = ""
payload_ = ""
payload_door = ""
payload_button = ""
payload_cal = ""
payload_start = ""
calibration = False
payload_id  = ""
strOrder = ""
order_id = ""




def on_message_id(client, userdata, msg):
  global payload_id
  payload_id  = json.loads(msg.payload)

def on_message_button(client, userdata, msg):
  global payload_button
  payload_button = json.loads(msg.payload)

def on_message_cal(client, userdata, msg):
  global payload_cal
  payload_cal = json.loads(msg.payload)

def on_message(client, userdata, msg):
  global payload_update
  payload_update = json.loads(msg.payload)

def on_message_w(client, userdata, msg):
  global payload_
  payload_ = json.loads(msg.payload)

def on_message_door(client, userdata, msg):
  global payload_door
  payload_door = json.loads(msg.payload)

def on_message_start(client, userdata, msg):
  global payload_start
  payload_start = json.loads(msg.payload)

broker = "mqtt.mqtzao.com"
broker_port = 1883
timeout_reconnect = 60

broker_topic_update = "shelf/update"


client_update = mqtt.Client()
client = mqtt_.Client()
client_door = mqtt_.Client()
client_button = mqtt_back.Client()
client_cal = mqtt_cal.Client()
client_id = mqtt_id.Client()
client_start = mqtt_start.Client()

client_update.on_message = on_message
client_door.on_message = on_message_door
client_button.on_message = on_message_button
client_cal.on_message = on_message_cal
client_id.on_message = on_message_id
client_start.on_message = on_message_start

client_door.connect('mqtt.mqtzao.com', broker_port, timeout_reconnect)
client_update.connect(broker, broker_port, timeout_reconnect)
client.connect(broker, broker_port, timeout_reconnect)
client_button.connect('mqtt.mqtzao.com', broker_port, timeout_reconnect)
client_cal.connect(broker, broker_port, timeout_reconnect)
client_start.connect("mqtt.mqtzao.com", broker_port, timeout_reconnect)

client_id.connect('mqtt.mqtzao.com', broker_port, timeout_reconnect)

client_update.subscribe(broker_topic_update, 0)
client_update.loop_start()
client_button.loop_start()
client_cal.loop_start()
client_id.loop_start()
client_start.loop_start()


if not EMULATE_HX711:
  import RPi.GPIO as GPIO
  from hx711 import HX711
else:
  from emulated_hx711 import HX711

def cleanAndExit():
  print("Cleaning...")

  if not EMULATE_HX711:
    GPIO.cleanup()

  print("Bye!")
  sys.exit()

def getserial():
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"
  return cpuserial

def restarTotalShelves():
  global shelves_count
  shelves_count = shelves_count + 1
  if(shelves_count == 10):
    url = "https://iot4retail.mydearlab.com/device/" + getserial() + "/total_shelves"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    global total_shelves
    total_shelves = len(json.loads(json.dumps(data))['response'])
    global shelves_count
    shelves_count = 0

#Shelves configuration
def getShelvesConfiguration():
  print("initialize..............")
  print(getserial())
  try:
    url = "https://iot4retail.mydearlab.com/device/" + getserial() + "/total_shelves"
    print(url)
    response = urllib.urlopen(url)
    print(response)
    data = json.loads(response.read())
    print(getserial())
    global total_shelves
    total_shelves = len(json.loads(json.dumps(data))['response'])
    print("Total shelves: ", total_shelves)
    for i in range(total_shelves):
      shelf_port.append(json.loads(json.dumps(data))['response'][i]['port'])
      shelf_position.append(json.loads(json.dumps(data))['response'][i]['position'])
      shelf_weigth.append(json.loads(json.dumps(data))['response'][i]['weigth'])
      shelf_product.append(json.loads(json.dumps(data))['response'][i]['product_id'])
      shelf_product_name.append(json.loads(json.dumps(data))['response'][i]['product_name'])
      shelf_ean.append(json.loads(json.dumps(data))['response'][i]['ean'])
      shelf_id.append(json.loads(json.dumps(data))['response'][i]['id'])
      shelf_device_id.append(json.loads(json.dumps(data))['response'][i]['device_id'])
      #print('duda 1')
      shelf_store_id.append(json.loads(json.dumps(data))['response'][i]['store_id'])
      shelf_store_cod.append(json.loads(json.dumps(data))['response'][i]['store_cod'])

      shelf_w_factor.append(json.loads(json.dumps(data))['response'][i]['w_factor'])
      shelf_v_factor.append(json.loads(json.dumps(data))['response'][i]['v_factor'])

      #print('duda 1')

      hx.append(HX711(shelf_port[i], 9))
      hx[i].set_reading_format("MSB", "MSB")
      hx[i].set_reference_unit(referenceUnit)
      hx[i].reset()
      hx[i].tare()
      print('Send MQTT...')
      broker_out_update  = {"device_id":str(shelf_device_id[0]), "value": "False"}
      data_out  = json.dumps(broker_out_update)
      print(data_out)
      client_update.publish(broker_topic_update, data_out, qos=2, retain=True)
      url = "https://iot4retail.mydearlab.com/device/" + getserial() + "/last_total/" + str(shelf_device_id[i]) + "/" + str(shelf_id[i])
      print(url)
      #response = []
      response_ = urllib.urlopen(url)
      #print(response)
      data_ = json.loads(str(response_.read()))
      print(data_)
      print('duda 01')

      total = int(float(str(json.loads(json.dumps(data_))['response']['total'])))
      print(total)
      print('**************************')

      mqtt_total.append(int(float((str(json.loads(json.dumps(data_))['response']['total'])))))

      weight_.append(int(float(str(json.loads(json.dumps(data_))['response']['weight']))))
      #print("mqtt_total: ",mqtt_total[i])
      #print("weight: ", weight_[i])
      print('----------------------')
      print(mqtt_total[i])
      print('duda b4')

      if((int(mqtt_total[i]) * int(shelf_weigth[i])) > 0):
        print('duda > 0')
        direction.append(int(False))
      else:
        print('duda else')
        direction.append(int(True))

      print("direction: ",direction[i])

  except:
    return "error"
  return total_shelves

getShelvesConfiguration()

def shelfRestart():
  try:
    if(json.loads(json.dumps(payload_update))['value'] == "True"):
      shelf_port = []
      shelf_weigth = []
      shelf_product = []
      shelf_position = []
      shelf_product_name = []
      shelf_ean = []
      shelf_id = []
      shelf_device_id = []
      shelf_store_id = []
      shelf_store_cod = []
      mqtt_total = []
      weight_= []
      direction = []
      door_status = []
      hx = []
      getShelvesConfiguration()
      reconnect_mode = True
      broker_out_update  = {"device_id":str(shelf_device_id[0]), "value": "False"}
      data_out  = json.dumps(broker_out_update)
      client_update.publish(broker_topic_update, data_out, qos=2, retain=True)
  except:
    return "error"

def getDoorStatus():
  try:
    global door_status
    door_status = []
    for i in range(total_shelves + 1):
      print("door_status: ")
      topic_button = "back/button/1"
      client_button.subscribe(topic_button, 2)
      door_status.insert(int(json.loads(json.dumps(payload_button))['door']), json.loads(json.dumps(payload_button))['status'])

      print('x1 --------------------------------------------------')
      global payload_button
      payload_button = ''
      topic_button = ''
      global payload_id
      topic_id = "back/button/event/" + getserial() 
      client_id.subscribe(topic_id, 2)
      print("payload_id: ", payload_id)
      global customer_id
      customer_id = json.loads(json.dumps(payload_id))['customer_id']

      print("doorStatus customer_id: ", customer_id)

      payload_id = ''
      topic_id = ''
      time.sleep(0.1)
  except:
    return "error"

def getCalibration():
  try:
    topic_cal = "shelf/calibrate/" + str(shelf_device_id[0])
    client_cal.subscribe(topic_cal, 2)
    status_cal = json.loads(json.dumps(payload_cal))['status']
    #print(status_cal)
    global payload_cal
    payload_cal = ''
    topic_cal = ''
    if(status_cal == 'on'):
      global calibration
      calibration = True
    else:
      global calibration
      calibration = False
    time.sleep(0.1)
  except:
    return "error"


def setCalibration():
    print("****************")
    print(shelf_device_id[0])
    broker_out_update  = {"status":"off"}
    data_out  = json.dumps(broker_out_update)
    client_update.publish("shelf/calibrate/" + str(shelf_device_id[0]), data_out, qos=2, retain=True)
    global calibration
    calibration = False
    #print('calibration off')

def weigthing():
  print("total shelf: ", total_shelves)
  shelf_weight_ = 0
  try:
    print('w step 1')
    restarTotalShelves()
    print('w step 2')
    global payload_id
    topic_id = "back/button/event/" + getserial()
    client_id.subscribe(topic_id, 2)
    print('w step 3')
    global customer_id
    customer_id = json.loads(json.dumps(payload_id))['customer_id']
    print('w step 4')
    print("customer_id: " + str(customer_id))
    print('############################')
    print('w step 5')
    for j in range(total_shelves):
      print("pesando...", shelf_position[j] )
      value.append(hx[j].get_weight(5) / (shelf_weigth[j] * shelf_w_factor[j]))
      weight_value = hx[j].get_weight(5)
      grams = (hx[j].get_weight(5) / shelf_w_factor[j])
      st = str(datetime.datetime.utcnow())
      product_value_weight = 0
      product_value_weight = (shelf_weigth[j] * shelf_w_factor[j])

      print('gabi 01')


      if(int(direction[j]) == 1):
        print('-------1')
        shelf_weight_ = weight_value
        grams = shelf_weight_ / shelf_w_factor[j]
      else:
        print('-------2')
        print(shelf_weight_)
        print(weight_[j])
        print(shelf_w_factor[j])
        print('.........')
        if(round(shelf_weight_) <= round(weight_[j] * shelf_w_factor[j])):
          print('-------3')
          shelf_weight_ = (weight_value) + (weight_[j] * shelf_w_factor[j])
        else:
          print('========4')
          shelf_weight_ = round(weight_value) + round((weight_[j]) * shelf_w_factor[j])
        grams = shelf_weight_ / shelf_w_factor[j]
      print('---------5')
      if(round(shelf_weight_) > round(product_value_weight)):
        print('aqui 1')
        abs_weight = round((shelf_weight_ / product_value_weight))
      else:
        if(shelf_weight_ <= 0):
          print('aqui 2')
          abs_weight = 0
        else:
          if(grams <= (shelf_weight_ * shelf_v_factor[j])):
           print('aqui 3')
           abs_weight = 0
          else:
           print('aqui 4')
           #abs_weight = round((grams / shelf_weight_))
           abs_weight = round((product_value_weight / shelf_weight_))


      print('----------------------')
      print('total: ', (shelf_weigth[j] * shelf_w_factor[j]))
      print('---------------------')


      if(grams == 0 or grams < (shelf_weigth[j] * shelf_w_factor[j])):
        abs_weight = 0

      if(grams >= (shelf_weigth[j] * shelf_w_factor[j])):
        abs_weight = round((grams / shelf_weight_))

      #product_value_weight = abs_weight


      #print('###########################')
      #delta_weight = (float(((shelf_weight_ - abs_weight) - ((shelf_weight_ - abs_weight)* shelf_v_factor[j]))/shelf_w_factor[j]) / shelf_weigth[j])

      delta_weight = (float( grams /  shelf_weigth[j]))
      

      #print('product_value_weight: ', product_value_weight)
      #print('abs_weight: ', abs_weight)
      #print('v_factor: ', v_factor)
      #delta_weight = abs(float(((product_value_weight - abs_weight) - ((product_value_weight - abs_weight)* v_factor))/w_factor) / shelf_weigth[j])
      ###########################
      abs_weight = round(abs(delta_weight))

      global strOrder

      #strOrder = md5(str(customer_id) + str(shelf_store_id[j]) + str(shelf_device_id[j]) + str(time.time())).hexdigest()
      strOrder = md5(str(customer_id) + str(shelf_store_id[j]) + str(shelf_device_id[j])).hexdigest()

      global order_id
      order_id = strOrder[0:8] + "-" + strOrder[8:16] + "-" + strOrder[16:24] + "-" + strOrder[24:32]
      broker_out  = {"order_id": order_id, "direction": str(direction[j]), "delta_weight": str(delta_weight), "last_total":str(mqtt_total[j]), "shelf_id":str(shelf_id[j]), "total":str(abs_weight), "weight":str(grams), "status_port": status_port_, "purchase_status_":str(purchase_status_), "customer_id":str(customer_id), "date": st, "device_id":str(shelf_device_id[j]), "store_id": str(shelf_store_id[j]), "shelf_product": str(shelf_product[j])}
      data_out  = json.dumps(broker_out)

      client_update.publish("shelf/content", data_out, qos=2, retain=True)
      client_update.publish("shelf/last/content/" + str(shelf_device_id[j]) + "/" + str(shelf_id[j]), data_out, qos=2, retain=True)


      if(calibration == False and len(str(customer_id)) > 0):
        broker_out  = {"order_id": order_id, "direction": str(direction[j]), "delta_weight": str(delta_weight), "last_total":str(mqtt_total[j]), "shelf_id":str(shelf_id[j]), "total":str(abs_weight), "weight":str(grams), "status_port": status_port_, "purchase_status_":str(purchase_status_), "customer_id":str(customer_id), "date": st, "device_id":str(shelf_device_id[j]), "store_id": str(shelf_store_id[j]), "shelf_product": str(shelf_product[j])}
        data_out  = json.dumps(broker_out)

        client_update.publish("shelf/last/content/" + str(shelf_device_id[j]) + "/" + str(shelf_id[j]), data_out, qos=2, retain=True)

        client_update.publish("shelf/content", data_out, qos=2, retain=True)
        #print(data_out)
        #print("customer_id: " + str(customer_id) + "  ::  j: " + str(j) + " :: Shelf: " + str(shelf_position[j]) + "  :: Total Items: " + str(abs_weight) + "  ::  T: " + str(abs((hx[j].get_weight(5) / shelf_w_factor[j]) / (product_value_weight / shelf_w_factor[j]))))

      #print("------------------------")
      #status_door = door_status[int(shelf_position[j])]
      #print("------------------------")
      #print("len: ", len(str(customer_id)))
      #print("pesagem customer_id: ", customer_id)
      #print("shelf_weigth: ", shelf_weigth[j])
      if(len(str(customer_id)) > 0):
        broker_out  = {"order_id": order_id, "direction": str(direction[j]), "delta_weight": str(delta_weight), "last_total":str(mqtt_total[j]), "shelf_id":str(shelf_id[j]), "total":str(abs_weight), "weight":str(grams), "status_port": status_port_, "purchase_status_":str(purchase_status_), "customer_id":str(customer_id), "date": st, "device_id":str(shelf_device_id[j]), "store_id": str(shelf_store_id[j]), "shelf_product": str(shelf_product[j])}
        data_out  = json.dumps(broker_out)
        #print("len: ", len(str(customer_id)))
        client_update.publish("shelf/content", data_out, qos=2, retain=True)
        print("customer_id: " + str(customer_id) + "  ::  j: " + str(j) + " :: Shelf: " + str(shelf_position[j]) + "  :: Total Items: " + str(abs_weight) + "  ::  T: " + str(abs((hx[j].get_weight(5) / shelf_w_factor[j]) / (product_value_weight / shelf_w_factor[j]))))

      hx[j].power_down()
      hx[j].power_up()

  except:
    return "error"


def restart():
  command = "/usr/bin/sudo /sbin/shutdown -r now"
  import subprocess
  process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
  output = process.communicate()[0]
  print output

while True:
  try:
    global payload_start
    client_start.subscribe('supervisor/initialize', 0)
    #print("aqui ", payload_start)
    client_start.loop_start()
    print("step 1")
    getDoorStatus()

    print("step 2")
    getCalibration()
    if(calibration == False):
      print('aqui False')
      weigthing()
      time.sleep(1)
      setCalibration()

    if(calibration == True):
      print('aqui true')
      shelfRestart()
      getShelvesConfiguration()
      setCalibration()

    client_door.subscribe('device/door', 0)
    client_door.loop_start()

    print("payload_door: ", payload_door)

    if(payload_door != ""):
      status_port_ = int(json.loads(json.dumps(payload_door))['status'])
      position_port_ = int(json.loads(json.dumps(payload_door))['position'])
      getShelvesConfiguration()

    reconnect_mode = False

    shelfRestart()

    time.sleep(0.8)

  except (KeyboardInterrupt, SystemExit):
    cleanAndExit()

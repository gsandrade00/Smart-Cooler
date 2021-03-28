import paho.mqtt.client as mqtt #import the client1
import paho.mqtt.client as mqtt_
import time
from datetime import datetime
import json
import os

payload_button = ""
status = ""
customer = ""
def on_message_button(client, userdata, msg):
  global payload_button
  payload_button = json.loads(msg.payload)

broker_address="mqtt.mqtzao.com"
client = mqtt.Client()
client_update = mqtt_.Client()

client.on_message = on_message_button

client.connect(broker_address)
client_update.connect(broker_address)
client.loop_start()
client_update.loop_start()

device_id = '00000000ef61f377'

def takePicture(customer):
  device_id = '00000000ef61f377'
  val_customer = customer[len(customer)-17:len(customer)]
  name = str(val_customer) + datetime.today().strftime('%Y%m%d%H%M%S') + '.jpg'
  cmd = 'fswebcam -r 1280x720 --no-banner /home/baby/images/' + name
  time.sleep(2)
  print(cmd)
  os.system(cmd)
  cmd = ''
  #cmd = 'curl -F "cart_image[customer_id=' + str(val_customer) + '" -F "cart_image[img_event=@/home/baby/images/' + name + '" https://iot4retail.mydearlab.com/cart_images'
  #cmd = "curl -F 'cart_image[customer_id=" + str(val_customer) + "' -F 'cart_image[image_event=@/home/baby/images/" + name + "' http://10.115.193.226:8899/cart_images"
  cmd = 'curl -F "cart_image[customer_id=' + str(val_customer) + '" -F "cart_image[device_id=' + device_id + '" -F "cart_image[img_event=@/home/baby/images/' + name + '" https://iot4retail.mydearlab.com/cart_images'

  print(cmd)
  os.system(cmd)
  time.sleep(1)
  cmd = ''
  cmd = 'rm -Rf /home/baby/images/' + name
  os.system(cmd)
  print(cmd)
  cmd = ''
  name = ''

while True:
  global payload_button
  client.subscribe("supervisor/photo/" + str(device_id))
  if(len(payload_button) > 0):
    global status
    global customer
    status = json.loads(json.dumps(payload_button))['status']
    customer = json.loads(json.dumps(payload_button))['customer_id']
    maintenance_ = json.loads(json.dumps(payload_button))['maintenance']

    if(maintenance_ == "true"):
      print("photo maintenance")
      takePicture('MAINTENANCE')
      broker_out_update  = {"status":"off","customer_id":"MAINTENANCE","event":"0","maintenance":"false"}
      data_out  = json.dumps(broker_out_update)
      print(data_out)
      client_update.publish("supervisor/photo/" + str(device_id), data_out, qos=2, retain=True)
      time.sleep(1)


    if(status == "on"):
      print("photo")
      takePicture(str(customer))
      time.sleep(1)
  payload_button = ""
  time.sleep(0.1) # wait
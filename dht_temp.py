import Adafruit_DHT

DHT_SENSOR = Adafruit_DHT.DHT22

DHT_PIN = 26



while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        print(temperature)
        print("/n")
        print(humidity)

#={0:0.1f}*C  Umidade={1:0.1f}%".format(temperature, h$
    else:
        print("Falha ao receber os dados do sensor de umidade")

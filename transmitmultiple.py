import paho.mqtt.client as paho
import random
from time import sleep



broker="127.0.0.1"
port=1883

def on_publish(client,userdata,result):
    print("data published \n")
    pass

client1= paho.Client("control1")
client1.on_publish = on_publish
client1.connect(broker,port)

while True:
    fake_data = [random.randint(0,1000),round(random.uniform(33.33, 66.66), 2),round(random.uniform(33.33, 66.66), 2),random.randint(0,100)] #Height, lat, lon, temp
    client1.publish("sensor/height", fake_data[0])
    client1.publish("sensor/lat", fake_data[1])
    client1.publish("sensor/lon", fake_data[2])
    client1.publish("sensor/temp", fake_data[3])
    sleep(1)
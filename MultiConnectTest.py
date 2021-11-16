import paho.mqtt.client as mqtt
import random
clients=[]
nclients=20
mqtt.Client.connected_flag=False
#create clients

broker = '127.0.0.1'
port = 1883
topic = "data/test"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'mqtt'
password = 'test'

for i  in range(nclients):
   cname="Client"+str(i)
   client= mqtt.Client(cname)
   clients.append(client)
for client in clients:
  client.connect(broker)
  client.loop_start()

import serial
import paho.mqtt.client as paho
import struct

broker="127.0.0.1"
port=1883

def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass

client1= paho.Client("control1")                           #create client object
client1.on_publish = on_publish                          #assign function to callback
client1.connect(broker,port)                                 #establish connection
                   #publish
ser = serial.Serial('COM7',11520)
serData = ser.readline().decode('utf-8')
#things = str.encode('b')
#ser.write(things)
#counter = 0

while True:
    serData = ser.readline().decode('utf-8')
    #imux,imuy,imuz = serData.split('\n')
    #print(imux,imuy,imuz)
    print(serData)
    payload = int(serData)
    ret= client1.publish("sensor/ServoAngle",payload)


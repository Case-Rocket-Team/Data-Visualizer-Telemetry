import serial

ser = serial.Serial('COM9',11520)
serData = ser.readline().decode('utf-8')
things = str.encode('b')
ser.write(things)
counter = 0

while True:
    serData = ser.readline().decode('utf-8')
    imux,imuy,imuz = serData.split(';')
    print(imux,imuy,imuz)
    #print(serData)


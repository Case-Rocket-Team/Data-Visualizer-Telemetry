#Import our many, many libraries!
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ctypes
import threading
import serial.tools.list_ports
import win32serviceutil as svc
import paho.mqtt.client as mqtt
import threading
from elevate import elevate

elevate(show_console=False) #Launches UAC prompt to run program as admin, lets us adjust Windows services (e.g. Grafana, Mosquitto)

#Variable Declarations
ports = serial.tools.list_ports.comports()
ser = serial.Serial()
serverStat = "Not Running"
serialStatus = "Not Connected"
bothRunning = None
appID = 'CRT.Telemetry.alpha1'
run2 = '#D13539'
broker="127.0.0.1" #MQTT Server
port=1883 #Server Port
goodBauds = (9600,14400,19200,115200)

#Freaky Windows Shit
ctypes.windll.shcore.SetProcessDpiAwareness(1) #Enables support for Hi-DPI displays.
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID) #Wizardry to make the taskbar icon to the main icon

#GUI Specific declarations
root = tk.Tk()
widget_var = tk.StringVar()
baudsel = tk.StringVar()

big_frame = ttk.Frame(root)
big_frame.pack(fill="both", expand=True)

photo = tk.PhotoImage(file='C:\\Users\\catsl\\Documents\\Telemtry Dash\\refresh.png')


#Functions in no particular order
def refreshPorts(): #Checks available COM Ports and lists in dropdown
    ports = serial.tools.list_ports.comports()
    COMdropdown['values'] = ports
    COMdropdown.current(0)

def connectPort(): #Connects to selected COM port
    comnum = COMdropdown.get()
    ser.baudrate = BaudSelect.get()
    ser.port = comnum[0:4]
    try:
        ser.open()
        messagebox.showinfo("Info","Connected successfully to " + comnum[0:4])
        button['state'] = tk.DISABLED
        button2['state'] = tk.NORMAL
        SerialConnected['foreground'] = '51B7EB'
        thread = threading.Thread(target=readData)
        thread.start()
    except serial.SerialException:
        messagebox.showerror("Error","Serial Error")

def closeSerial(): #Disconnects from serial
    button2['state'] = tk.DISABLED
    button['state'] = tk.NORMAL
    comnum = COMdropdown.get()
    try:
        ser.close()
        messagebox.showinfo("Info","Disconnected successfully from " + comnum[0:4])
        run2 = '#D13539'
    except serial.SerialException:
        messagebox.showerror("Error","Unable to close serial connection")  

def defaultBaud(): #Sets default baud rate, could do some trickery here to determine fastest/best connection. Hard coded atm
    BaudSelect.current(1) 

def startServices(): #Starts Grafana and Mosquitto Broker
    try:
        print("Starting Services...")
        svc.StartService("grafana")
        svc.StartService("mosquitto")
        messagebox.showinfo("Info","Services Started!")
        serverStat = "Running"
        SerialConnected.config(text="Serial Connected: Connected",foreground="51B7EB")
    except:
        messagebox.showerror("Error","Unable to start services")
    
    
    
def stopServices():#Stops Grafana and Mosquitto Broker
    print("Stopping Services...")
    try:
        svc.StopService("grafana")
        svc.StopService("mosquitto")
        serverStat = "Not Running"
        messagebox.showinfo("Info","Services Stopped!")
    except:
        messagebox.showerror("Error","Unable to stop services")

def setIcon(): #Sets icon
    root.iconbitmap('C:\\Users\\catsl\\Documents\\Telemtry Dash\\icon.ico')

def checkIfRunning(): #Attempts to see if services are already running. Doesn't work yet
    try: 
        svc.QueryServiceStatus('grafana')
        svc.QueryServiceStatus('mosquitto')
    except:
        bothRunning = False
    else:
        bothRunning = True

def handle_data(data): #Processes serial data
    print(data)

def readData(): #Reads serial data
    while True:
        serData = ser.readline()
        handle_data(serData)

def on_publish(client,userdata,result): #Callback function for MQTT
    print("data published \n")
    pass

#Logic that doesn't quite work yet
if bothRunning == True:
    run1 = '#51B7EB'
else:
    run1 = '#D13539'

#Create UI
root.tk.call("source", "C:\\Users\\catsl\\Documents\\Telemtry Dash\\Sun-Valley-ttk-theme-master\sun-valley.tcl")
root.tk.call("set_theme", "dark")
root.resizable(False, False)
root.title("Telemetry - Serial to MQTT")
root.geometry("625x300")
root.after(0,setIcon)

#UI Elements
button = ttk.Button(big_frame, text="Connect",command=connectPort,style="Accent.TButton")
button.place(x=475,y=25)
button.config(width=10)

button2 = ttk.Button(big_frame, text="Disconnect",command=closeSerial,style="Accent.TButton",state=tk.DISABLED)
button2.place(x=475,y=80)
button2.config(width=10)

button3 = ttk.Button(big_frame, text="Start Services ✅",command=startServices)
button3.place(x=435,y=160)

button4 = ttk.Button(big_frame, text="Stop Services 🛑",command=stopServices)
button4.place(x=435,y=230)

button5 = ttk.Button(big_frame, image = photo,command=refreshPorts,style="Accent.TButton")
button5.place(x=405,y=25)

COMdropdown = ttk.Combobox(big_frame,textvariable=widget_var)
BaudSelect = ttk.Combobox(big_frame,textvariable=baudsel)

MQTTConnected = ttk.Label(root, text="MQTT Server: " + serverStat,foreground=run1)
GrafConnected = ttk.Label(root, text="Grafana Service: " + serverStat,foreground=run1)
SerialConnected = ttk.Label(root, text="Serial Connected: " + serialStatus,foreground=run2)

COMdropdown['values'] = ports #Populates COM Dropdown with available ports

try:
    COMdropdown.current(0) #Attempts to list available port as first option
except:
    COMdropdown.set("Select COM Port")

COMdropdown['state'] = 'readonly'
BaudSelect.set("Select Baud Rate")
BaudSelect['values'] = goodBauds
BaudSelect['state'] = 'readonly'

#Configures and sizes certain widgets
COMdropdown.config(width=30)
BaudSelect.config(width=36)
COMdropdown.place(x=25,y=25)
BaudSelect.place(x=25,y=80)
MQTTConnected.place(x=25,y=160)
GrafConnected.place(x=25,y=200)
SerialConnected.place(x=25,y=240)

root.mainloop() #Keeps our UI updating
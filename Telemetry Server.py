#Import libraries
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ctypes
import threading
import serial.tools.list_ports
import win32serviceutil as svc
import paho.mqtt.client as mqtt
import threading
import logging
from elevate import elevate

#Set up logging functionality
logPath = 'C:\\Users\\catsl\\Documents\\Telemtry Dash\\log.txt'

logging.basicConfig(filename=logPath,
                            filemode='w',
                            format='%(asctime)s| %(levelname)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S',
                            level=logging.DEBUG)
logging.info('Imports complete')

try:
    elevate(show_console=False) #Launches UAC prompt to run program as admin, lets us adjust Windows services (e.g. Grafana, Mosquitto)
    logging.info('Successfully elevated privileges')
except Exception as e:
    logging.critical("Failed to elevate privileges. Program will not run properly.")
    logging.critical("Elevate Error: " + str(e))
    messagebox.showerror("Critical Error",
    "Program is not run as administator and will not function as intended. Please rerun with approriate permissions.")
    exit()

#Variable Declarations
appID = 'CRT.Telemetry.alpha1'

ports = serial.tools.list_ports.comports()
ser = serial.Serial()
goodBauds = (9600,14400,19200,115200)

serverStat = "Not Running"
serialStatus = "Not Connected"
bothRunning = None
run1 = '#51B7EB'
run2 = '#D13539'

broker="127.0.0.1" #MQTT Server
port=1883 #Server Port

#Freaky Windows Shit
ctypes.windll.shcore.SetProcessDpiAwareness(1) #Enables support for Hi-DPI displays.
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID) #Wizardry to make the taskbar icon to the main icon
logging.debug("Mischief managed :)")

#GUI Specific declarations
ui = tk.Tk()
widget_var = tk.StringVar()
baudsel = tk.StringVar()

big_frame = ttk.Frame(ui)
big_frame.pack(fill="both", expand=True)

try:
    photo = tk.PhotoImage(file='C:\\Users\\catsl\\Documents\\Telemtry Dash\\refresh.png')
except:
    logging.error("Unable to import button icon. Does file exist?")


#Functions in no particular order
def refreshPorts(): #Checks available COM Ports and lists in dropdown
    ports = serial.tools.list_ports.comports()
    COMdropdown['values'] = ports
    #COMdropdown.current(0)
    try:
        COMdropdown.current(0) #Attempts to list available port as first option
    except:
        COMdropdown.set("Select COM Port")
    ui.after(1000,refreshPorts)

def connectPort(): #Connects to selected COM port
    comnum = COMdropdown.get()
    ser.baudrate = BaudSelect.get()
    ser.port = comnum[0:5]
    try:
        ser.open()
        messagebox.showinfo("Info","Connected successfully to " + comnum[0:4])
        button['state'] = tk.DISABLED
        button2['state'] = tk.NORMAL
        SerialConnected['foreground'] = '#51B7EB'
        SerialConnected['text'] = 'Serial: Connected'
        thread = threading.Thread(target=readData, daemon=True)
        thread.start()
    except serial.SerialException as e:
        messagebox.showerror("Serial Error",e)
        logging.error("Serial error " + str(e))

def closeSerial(): #Disconnects from serial
    button2['state'] = tk.DISABLED
    button['state'] = tk.NORMAL
    comnum = COMdropdown.get()
    try:
        ser.close()
        messagebox.showinfo("Info","Disconnected successfully from " + comnum[0:4])
        SerialConnected['foreground'] = '#D13539'
        SerialConnected['text'] = 'Serial: Not Connected'
        COMdropdown.set("Select COM Port")
    except serial.SerialException as e:
        logging.error("Serial error " + str(e))
        messagebox.showerror("Serial Error","Unable to close serial connection: " + str(e))  

def defaultBaud(): #Picks 9600 baud as a safe bet
    BaudSelect.current(1) 

def startServices(): #Starts Grafana and Mosquitto Broker
    try:
        logging.info("Starting Services...")
        svc.StartService("grafana")
        svc.StartService("mosquitto")
        messagebox.showinfo("Info","Services Started!")
        MQTTConnected["text"] = "MQTT Server: Running"
        GrafConnected["text"] = "Grafana Service: Running"
        MQTTConnected["foreground"] = "#51B7EB"
        GrafConnected["foreground"] = "#51B7EB"
        logging.info("Services Started")
    except:
        messagebox.showerror("Error","Unable to start services or services already running.")
        logging.error("Unable to start services or services already running.")
    
    
def stopServices():#Stops Grafana and Mosquitto Broker
    logging.info("Stopping Services...")
    try:
        svc.StopService("grafana")
        svc.StopService("mosquitto")
        serverStat = "Not Running"
        messagebox.showinfo("Info","Services Stopped!")
        MQTTConnected["text"] = "MQTT Server: Not Running"
        GrafConnected["text"] = "Grafana Service: Not Running"
        MQTTConnected["foreground"] = "#D13539"
        GrafConnected["foreground"] = "#D13539"
        logging.info("Services Stopped")
    except:
        messagebox.showerror("Error","Unable to stop services or services already stopped.")
        logging.error("Unable to stop services or services already stopped.")

def setIcon(): #Sets icon
    try:
        ui.iconbitmap('C:\\Users\\catsl\\Documents\\Telemtry Dash\\icon.ico')
    except:
        logging.warning("Unable to set icon. Does file exist?")

def getServerStatus(): #Attempts to see if services are already running. Doesn't work yet
    grafStatus = svc.QueryServiceStatus('grafana')
    mosqStatus = svc.QueryServiceStatus('mosquitto')
    global grafServer
    global mosqServer
    global run1
    if grafStatus[1] == 1:
        grafServer = "Not Running"
        run1 = "#D13539"
    elif grafStatus[1] == 4:
        grafServer = "Running"
        run1 = '#51B7EB'
    if mosqStatus[1] == 1:
        mosqServer = "Not Running"
    elif mosqStatus[1] == 4:
        mosqServer = "Running"
    ui.after(1000,getServerStatus)
 
def handle_data(data): #Processes serial data
    print(data)

def readData(): #Reads serial data
    while True:
        serData = ser.readline()
        handle_data(serData)

def on_publish(client,userdata,result): #Callback function for MQTT
    print("data published \n")
    pass

#Run just for good measure, not sure if it will if I don't
getServerStatus()

#Create UI
try:
    ui.tk.call("source", "C:\\Users\\catsl\\Documents\\Telemtry Dash\\Sun-Valley-ttk-theme-master\sun-valley.tcl")
    ui.tk.call("set_theme", "dark")
except Exception as e:
    logging.warning("Unable to set Tkinter theme. Error: " + str(e))

ui.resizable(False, False)
ui.title("Telemetry - Serial to MQTT")
ui.geometry("625x300")
ui.after(0,setIcon)
logging.info('UI Created')

#Buttons
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

#Dropdowns
COMdropdown = ttk.Combobox(big_frame,textvariable=widget_var)
BaudSelect = ttk.Combobox(big_frame,textvariable=baudsel)

#Labels
MQTTConnected = ttk.Label(ui, text="MQTT Server: " + mosqServer,foreground=run1)
GrafConnected = ttk.Label(ui, text="Grafana Service: " + grafServer,foreground=run1)
SerialConnected = ttk.Label(ui, text="Serial: " + serialStatus,foreground=run2)

#Configure dropdowns and labels
COMdropdown['values'] = ports #Populates COM Dropdown with available ports
COMdropdown['state'] = 'readonly'
COMdropdown.config(width=30)
COMdropdown.place(x=25,y=25)

BaudSelect.set("Select Baud Rate")
BaudSelect['values'] = goodBauds
BaudSelect['state'] = 'readonly'
BaudSelect.config(width=36)
BaudSelect.place(x=25,y=80)

MQTTConnected.place(x=25,y=160)
GrafConnected.place(x=25,y=200)
SerialConnected.place(x=25,y=240)

#Loop Functions
ui.after(1000,refreshPorts) #Autorefreshes COM port dropdown every second
ui.mainloop()
logging.info("Program exited")
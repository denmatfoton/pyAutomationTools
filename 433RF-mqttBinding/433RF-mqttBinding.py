import os
import sys
from collections import deque
import threading
import paho.mqtt.client as mqtt
from readXml import readDevicesFromXml

pathToRFCodeSender = "/home/pi/smarthome/433RF/RFCodeSender"
pathToRFCodes = "/home/pi/smarthome/433RF/rfcodes.bin"
xmlFile = "/home/pi/smarthome/scripts/433RF-mqttBinding/433RF-mqtt.xml"
#xmlFile = "433RF-mqtt.xml"

if not os.path.isfile(xmlFile):
    sys.exit(1)

devices = readDevicesFromXml(xmlFile)
cmdQueue = deque([])
semaphore = threading.Semaphore(0)
mutex = threading.Lock()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for device in devices.keys():
        client.subscribe(device)


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    codes = devices.get(msg.topic)
    if codes is not None:
        code = codes.get(msg.payload)
        if code is not None:
            cmd = '{} {} {}'.format(pathToRFCodeSender, code, pathToRFCodes)
            mutex.acquire()
            cmdQueue.append(cmd)
            mutex.release()
            semaphore.release()


def dispatch_cmd():
    while True:
        semaphore.acquire()
        mutex.acquire()
        cmd = cmdQueue.popleft()
        mutex.release()
        os.system(cmd)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
#client.connect("192.168.0.100", 1883, 60)

cmdDispatcher = threading.Thread(target=dispatch_cmd)
cmdDispatcher.start()

client.loop_forever()

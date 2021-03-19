# Monitor the rpm through a light barrier
# report the results back to AWS IOT core
# Version 3.0
# last update March 19, 2021

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

import json
import psutil
import argparse
import logging
import time

#########
# Imports for StirlingDevice
#########
from gpiozero import CPUTemperature
# rpm sensor related
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
####################
# Imports for temperature sensor
################################
#import os
import Adafruit_DHT

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

#########
# Variables StirlingDevice
#########
old_time = 0.0
timeouts = 0
old_period = 0
#running = 0
trigger = 0
# a list of periods sampled in a interval
rpmlist = []
# a list of accelerations sampled in a interval
accellist = []
#########

# add measurements to a list
def addtolist (newperiod,newaccel):
   global rpmlist
   global accellist
   rpmlist.append(newperiod)
   accellist.append(newaccel)

# calculate the averages and reset lists
def listaverage():
   global rpmlist
   global accellist
   sumrpm = 0.0
   i = 0
   for x in rpmlist:
     sumrpm = sumrpm + x
     i = i +1
   sumaccel = 0.0
   i = 0
   for x in accellist:
     sumaccel = sumaccel + x
     i = i +1
   resultrpm   = round(sumrpm / i)
   resultaccel = round(sumaccel / i,4)
   # reset the lists
   rpmlist = []
   accellist = []
   return { "rpm" : resultrpm, "acceleration" : resultaccel }


# Callback for rpm
def my_callback(channel):
    global old_time
    global old_period
    global trigger
    #period = 0.0
    new_time = time.time()
    period = new_time - old_time
    rpm = round(60/period)
    accelerate = round((old_period-period),6)
    # Catching errors
    # rpm is to high...
    if rpm >= 250: 
       print("***** Error, rpm:{:10.2f}     ***********".format(rpm))
       rpm = 0
    addtolist(rpm,accelerate)
    # Tracing
    #print(" acc  {:10.6f}     ***********".format(accelerate))
    #print(" per  {:10.6f}     ***********".format(period))
    #print(" olp  {:10.6f}     ***********".format(old_period))
    old_time = new_time
    old_period = period
    trigger = 1

    #print(" New  %    rpm ***********" % (rpm))

# Configures the argument parser for this program.
def configureParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host",
            help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", required=True, dest="certificatePath",
            help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", required=True, dest="privateKeyPath",
            help="Private key file path")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, default=8883,
            help="Port number override")
    parser.add_argument("-n", "--thingName", action="store", required=True, dest="thingName",
            help="Targeted thing name")
    parser.add_argument("-d", "--requestDelay", action="store", dest="requestDelay", type=float, default=1,
            help="Time between requests (in seconds)")
    parser.add_argument("-v", "--enableLogging", action="store_true", dest="enableLogging",
            help="Enable logging for the AWS IoT Device SDK for Python")
    return parser


# An MQTT shadow client that uploads device performance data to AWS IoT at a regular interval.
class PerformanceShadowClient:
    def __init__(self, thingName, host, port, rootCAPath, privateKeyPath, certificatePath, requestDelay):
        self.thingName = thingName
        self.host = host
        self.port = port
        self.rootCAPath = rootCAPath
        self.privateKeyPath = privateKeyPath
        self.certificatePath = certificatePath
        self.requestDelay = requestDelay

    # Updates this thing's shadow with system performance data at a regular interval.
    def run(self):
        print("Connecting MQTT client for {}...".format(self.thingName))
        mqttClient = self.configureMQTTClient()
        mqttClient.connect()
        print("MQTT client for {} connected".format(self.thingName))
        deviceShadowHandler = mqttClient.createShadowHandlerWithName(self.thingName, True)

        print("Running performance shadow client for {}...\n".format(self.thingName))
        while True:
            performance = self.readPerformance()
            print("[{}]".format(self.thingName))
            print("CPU:\t{}%".format(performance["cpu"]))
            print("Memory:\t{}%".format(performance["memory"]))
            print("mqtt_time_outs:\t{}".format(performance["mqtt_time_outs"]))
            print("raspberrytemp: \t{}".format(performance["raspberrytemp"]))
            print("rpm:           \t{}".format(performance["rpm"]))
            print("running:       \t{}".format(performance["running"]))
            print("accelerate:    \t{}".format(performance["accelerate"]))
            print("stirlingtemp:  \t{}\n".format(performance["stirlingtemp"]))
            payload = { "state": { "reported": performance } }
            deviceShadowHandler.shadowUpdate(json.dumps(payload), self.shadowUpdateCallback, 5)
            time.sleep(args.requestDelay)

    # Configures the MQTT shadow client for this thing.
    def configureMQTTClient(self):
        mqttClient = AWSIoTMQTTShadowClient(self.thingName)
        mqttClient.configureEndpoint(self.host, self.port)
        mqttClient.configureCredentials(self.rootCAPath, self.privateKeyPath, self.certificatePath)
        mqttClient.configureAutoReconnectBackoffTime(1, 32, 20)
        mqttClient.configureConnectDisconnectTimeout(10)
        mqttClient.configureMQTTOperationTimeout(5)
        return mqttClient

    # Returns the local device's CPU usage, memory usage, and timestamp.
    def readPerformance(self):
        #global rpm
        global trigger
        #global accelerate
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent

        # Determine CPU temparature of raspberry
        cputemp = CPUTemperature()
        raspberrytemp = cputemp.temperature

        if trigger == 0:  
           # first iteration. We just started
           rpm = 0
           accelerate = 0
        else:
            # we are in regular operations
            listresults = listaverage()
            rpm        = listresults["rpm"] 
            accelerate = listresults["acceleration"]
            if (accelerate > 0): accelerate =  1
            else:
               if (accelerate < 0): accelerate = -1
               else:                accelerate = 0
        trigger = 0
        if rpm == 0:  
           running = 0
           accelerate = 0
        else: running = 1

        #humidity, stirlingtemp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        #stirlingtemp = round(stirlingtemp,1)
        stirlingtemp = 21
        timestamp = time.time()
        
        return { "cpu": cpu, "memory": memory, "timestamp": timestamp, "mqtt_time_outs": timeouts, "raspberrytemp": raspberrytemp, "rpm": rpm, "running": running, "accelerate": accelerate, "stirlingtemp": stirlingtemp }
    
    # Prints the result of a shadow update call.
    def shadowUpdateCallback(self, payload, responseStatus, token):
        if responseStatus == "timeout":
           global timeouts
           timeouts = timeouts + 1

        print("[{}]".format(self.thingName))
        print("Update request {} {}\n".format(token, responseStatus))


# Configures debug logging for the AWS IoT Device SDK for Python.
def configureLogging():
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


# Runs the performance shadow client with user arguments.

# GPIO 24 set up as an input, pulled down, connected to 3V3 on button press
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# when a falling edge is detected on port 24, regardless of whatever
# else is happening in the program, the function my_callback will be run

GPIO.add_event_detect(24, GPIO.FALLING, callback=my_callback, bouncetime=300)

if __name__ == "__main__":
    parser = configureParser()
    args = parser.parse_args()
    if (args.enableLogging):
        configureLogging()
    thingClient = PerformanceShadowClient(args.thingName, args.host, args.port, args.rootCAPath, args.privateKeyPath,
            args.certificatePath, args.requestDelay)
    thingClient.run()


# main.py -- put your code here!
from login_secrets import (wifi_ssid, 
                           wifi_password, 
                           mqtt_port,
                           mqtt_server,
                           mqtt_user,
                           mqtt_password)
   
from umqttsimple import MQTTClient

# Get unique id from these libs
import ubinascii
import machine
import time

# Initialize comms
from uartremote import *
st = UartRemote()

KEEP_ALIVE = 5 	# Seconds to keep the connection alive after last publish/update command
                # Also used as timeout to detect when the robot goes offline
client_id = ubinascii.hexlify(machine.unique_id())
topic_root = b'beekeepers/'+ client_id + b'/'
topics = {
    'status' : topic_root+b'status',
    'command': topic_root+b'command',
    'response': topic_root+b'response'
    }

mqtt_client = MQTTClient(client_id, 
                            mqtt_server, 
                            mqtt_port,
                            mqtt_user,
                            mqtt_password,
                            keepalive = KEEP_ALIVE # Seconds
                         ) 
mqtt_client.set_last_will(topics['status'], b'Offline', retain=True, qos=2)

command = ""
args = []

# connect to wifi
def connect_wifi():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(wifi_ssid, wifi_password)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    

def sub_callback(topic, msg):
    global command, args
    print((topic, msg))
    if topic == topics['command']:
        if not b"," in msg:
            command = msg.decode("UTF-8")
            args = []
        else:
            items = msg.decode("UTF-8").split(",")
            command = items[0]
            args = [ eval(arg) for arg in items[1:] ]

mqtt_client.set_callback(sub_callback)

def connect_mqtt():
    result = None
    try:
        result = mqtt_client.connect()
        mqtt_client.publish(topics['status'], b'Ready', retain=True)        
        mqtt_client.subscribe(topics['command'])
        
    except OSError as e:
        result = e
    print('Connected to %s MQTT broker with result %s' % (mqtt_server, result))



connect_wifi()
connect_mqtt()
last_update = time.ticks_ms()
count=0
while 1:
    try:
        mqtt_client.check_msg()
        if command:
            mqtt_client.publish(topics['status'], b'Busy')
            time.sleep_ms(100)
            resp = st.call(command, *args, timeout=1500000)
            mqtt_client.publish(topics['response'], repr(resp)) #repr((command,args)))
            mqtt_client.publish(topics['status'], b'Ready')
            command = ""
            args = []
            last_update = time.ticks_ms()
        if time.ticks_ms() > last_update + KEEP_ALIVE*900:
            #mqtt_client.publish(topics['status'], 'Ready %s' % count, retain=True)
            #count +=1
            mqtt_client.publish(topics['status'], 'Ready')
            last_update = time.ticks_ms()
    except OSError as e:
        print("Reconnecting...")
        connect_mqtt()
        
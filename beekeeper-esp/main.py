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

# Initialize comms
from uartremote import *
st = UartRemote()

client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'robot/command'
topic_pub_stats= b'robot/status/'+client_id
topic_pub_last_will= b'robot/status/'+client_id+'/online'

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
    print((topic, msg))
    if topic == b'robot/command':
        st.call(msg.decode("UTF-8"))

def get_mqtt_client():
    try:
        # keepalive 20s; after that last will is transmitted by mqtt broker
        client = MQTTClient(client_id, 
                            mqtt_server, 
                            mqtt_port,
                            mqtt_user,
                            mqtt_password,
                            keepalive=20)
        client.connect()
    except OSError as e:
        print(e)
        return None

    client.set_callback(sub_callback)

    # Set last will to write b'False' when robot goes offline.
    client.set_last_will(topic_pub_last_will, b'False', retain=True)
    
    client.subscribe(topic_sub)
    client.publish(topic_pub_last_will, b'True')
    # print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

connect_wifi()
mqtt_client = get_mqtt_client()
while 1:
    try:
        mqtt_client.check_msg()
    except OSError as e:
        print("Reconnecting...")
        mqtt_client = get_mqtt_client()



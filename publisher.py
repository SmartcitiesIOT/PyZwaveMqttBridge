import logging
import sys, os
import resource
import paho.mqtt.client as mqtt
import time
import json
import datetime

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "base"
def on_publish(client, userdata, mid):
    print "Message Published..."

def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC)
    client.publish(MQTT_TOPIC, MQTT_MSG)

def on_message(client, userdata, msg):
    print(msg.topic)
    print(msg.payload) # <- do you mean this payload = {...} ?
    payload = json.loads(msg.payload) # you can use json.loads to convert string to json
    print(payload) # then you can check the value
    client.disconnect() # Got message then disconnect

poll_time = 1 #change sensor polltime
mqttc = mqtt.Client()
mqttc.on_publish = on_publish
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

#logging.getLogger('openzwave').addHandler(logging.NullHandler())
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('openzwave')

import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import time

device="/dev/ttyACM0"
log="Debug"

for arg in sys.argv:
    if arg.startswith("--device"):
        temp,device = arg.split("=")
    elif arg.startswith("--log"):
        temp,log = arg.split("=")
    elif arg.startswith("--help"):
        print("help : ")
        print("  --device=/dev/yourdevice ")
        print("  --log=Info|Debug")

#Define some manager options
options = ZWaveOption(device, \
  config_path="/usr/local/lib/python2.7/dist-packages/python_openzwave/ozw_config/config", \
  user_path=".", cmd_line="")
options.set_log_file("OZW_Log.log")
options.set_append_log_file(False)
options.set_console_output(False)
options.set_save_log_level(log)
#options.set_save_log_level('Info')
options.set_logging(False)
options.lock()

print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))

#Create a network object
network = ZWaveNetwork(options, log=None)

time_started = 0
print("------------------------------------------------------------")
print("Waiting for network awaked : ")
print("------------------------------------------------------------")
for i in range(0,300):
    if network.state>=network.STATE_AWAKED:

        print(" done")
        print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))
        break
    else:
        sys.stdout.write(".")
        sys.stdout.flush()
        time_started += 1
        time.sleep(1.0)
if network.state<network.STATE_AWAKED:
    print(".")
    print("Network is not awake but continue anyway")
print("------------------------------------------------------------")
print("Network home id : {}".format(network.home_id_str))
print("Controller node id : {}".format(network.controller.node.node_id))
print("Controller node version : {}".format(network.controller.node.version))
print("Nodes in network : {}".format(network.nodes_count))
print("------------------------------------------------------------")
print("Waiting for network ready : ")
print("------------------------------------------------------------")
for i in range(0,300):
    if network.state>=network.STATE_READY:
        print(" done in {} seconds".format(time_started))
        break
    else:
        sys.stdout.write(".")
        time_started += 1
        #sys.stdout.write(network.state_str)
        #sys.stdout.write("(")
        #sys.stdout.write(str(network.nodes_count))
        #sys.stdout.write(")")
        #sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1.0)


print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))
if not network.is_ready:
    print(".")
    print("Network is not ready but continue anyway")

print("------------------------------------------------------------")
print("Driver statistics : {}".format(network.controller.stats))
print("------------------------------------------------------------")

print("------------------------------------------------------------")
print("Try to autodetect nodes on the network")
print("------------------------------------------------------------")
print("Nodes in network : {}".format(network.nodes_count))
print("------------------------------------------------------------")
print("Retrieve sensors on the network")
print("------------------------------------------------------------")
values = {}
node = 2
while 1:

    MQTT_MSG = json.dumps({"time":str(datetime.datetime.now())})
    mqttc.publish(MQTT_TOPIC,MQTT_MSG)
    for val in network.nodes[node].get_sensors() :
        print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
        print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
        print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
        print("  value: {} {}".format(network.nodes[node].get_sensor_value(val), network.nodes[node].values[val].units))
        MQTT_MSG = json.dumps({network.nodes[node].values[val].label:network.nodes[node].get_sensor_value(val)})
        mqttc.publish(MQTT_TOPIC,MQTT_MSG)
    print("------------------------------------------------------------")
    print("Retrieve battery compatibles devices on the network         ")
    print("------------------------------------------------------------")
    values = {}
    for val in network.nodes[node].get_battery_levels() :
        print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
        print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
        print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
        print("  value : {}".format(network.nodes[node].get_battery_level(val)))
        MQTT_MSG = json.dumps({network.nodes[node].values[val].label:network.nodes[node].get_battery_level(val)})
        mqttc.publish(MQTT_TOPIC,MQTT_MSG)
    time.sleep(poll_time)
print("------------------------------------------------------------")


print("------------------------------------------------------------")
print("Driver statistics : {}".format(network.controller.stats))
print("Driver label : {}".format(network.controller.get_stats_label('retries')))
print("------------------------------------------------------------")

print("------------------------------------------------------------")
print("Stop network")
print("------------------------------------------------------------")
network.stop()
print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))


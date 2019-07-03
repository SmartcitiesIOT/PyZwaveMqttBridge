# PyZwaveMqttBridge

Requires:
MQTT broker running

Python OpenZwave <-> MQTT bridge, ready to use on rasberry pi with Zwave Stick
polls sensors every second and publishes them on topic "base"


Start camera with :
mjpg_streamer -i "./input_uvc.so -d /dev/video0 -n" -o "./output_http.so -p 8090 -w /usr/local/www"

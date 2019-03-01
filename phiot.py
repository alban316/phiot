#!/usr/bin/env python

from RPi import GPIO
import time
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
from datetime import datetime
import json

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED_ID = {'red':1, 'blue':2, 'green':4}
LED_PIN = [23,24,25]
PHOTO_PIN = 18

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
BASE_CONNECTION_STRING = "HostName={0};DeviceId={1};SharedAccessKey={2}"

# Using the MQTT protocol.
PROTOCOL = IoTHubTransportProvider.MQTT
MESSAGE_TIMEOUT = 10000

# Define the JSON message to send to IoT Hub.
MSG_TXT = '{"sensor_value" : %d, "time_stamp" : %s}'
INTERVAL = 1


map(lambda led: GPIO.setup(led, GPIO.OUT), LED_PIN)


#def init_leds():
#    map(lambda led: GPIO.setup(led, GPIO.OUT), LED_PIN)
#    set_leds(0)


def set_leds(mask):
    map(lambda i: GPIO.output(LED_PIN[i], mask & pow(2,i) == pow(2,i)), range(len(LED_PIN)))


def rc_time():
    reading = 0
    GPIO.setup(PHOTO_PIN, GPIO.OUT)
    GPIO.output(PHOTO_PIN, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(PHOTO_PIN, GPIO.IN)

    while (GPIO.input(PHOTO_PIN) == GPIO.LOW):
	reading += 1

    return reading


def send_confirmation_callback(message, result, user_context):
    print ( "IoT Hub responded to message with status: %s" % (result) )


def iothub_client_init(conn):
    # Create an IoT Hub client
    client = IoTHubClient(conn, PROTOCOL)
    return client


def device_method_callback(method_name, payload, user_context):
    # Handle direct method calls from IoT Hub    
    global INTERVAL
    print ( "\nMethod callback called with:\nmethodName = %s\npayload = %s" % (method_name, payload) )
    device_method_return_value = DeviceMethodReturnValue()
    if method_name == "SetTelemetryInterval":
        try:
            INTERVAL = int(payload)
            # Build and send the acknowledgment.
            device_method_return_value.response = "{ \"Response\": \"Executed direct method %s\" }" % method_name
            device_method_return_value.status = 200
        except ValueError:
            # Build and send an error response.
            device_method_return_value.response = "{ \"Response\": \"Invalid parameter\" }"
            device_method_return_value.status = 400
    else:
        # Build and send an error response.
        device_method_return_value.response = "{ \"Response\": \"Direct method not defined: %s\" }" % method_name
        device_method_return_value.status = 404

    return device_method_return_value


if __name__ == '__main__':
    try:
        with open('./config.json', 'r') as config_file:
            config = json.load(config_file)

        conn = BASE_CONNECTION_STRING.format(config['HostName'], config['DeviceId'], config['SharedAccessKey'])
        client = iothub_client_init(conn)

        # Set up the callback method for direct method calls from the hub.
        client.set_device_method_callback(
            device_method_callback, None)

        #initialize device indicators
        set_leds(0)

        #iitialize tick_count (used for throttling)
        last_tick = datetime.now()

        while True:
            sensor_value = rc_time()
            tick_now = datetime.now()

            if sensor_value < 300:
                sensor_state = LED_ID['green']

            elif sensor_value < 900:
                sensor_state = LED_ID['blue']

            else:
                sensor_state = LED_ID['red']

            # Build the message with telemetry values.
            message = IoTHubMessage(MSG_TXT % (sensor_value, str(tick_now)))

            # Add a custom application property to the message.
            # An IoT hub can filter on these properties without access to the message body.
            prop_map = message.properties()
            prop_map.add("sensor_state", sensor_state)

            # set device indicator 
            set_leds[sensor_state]

            # only send 2x/second since I'm on free tier w/ max 8000 messages/day
            if (tick_now - tick_last).microsecond > 500000:
                tick_last = tick_now
                client.send_event_async(message, send_confirmation_callback, None)

    except IoTHubError as iothub_error:
        print "Unexpected error %s from IoTHub" % iothub_error

    except KeyboardInterrupt:
        print "IoTHubClient sample stopped"

    finally:
        set_leds(0)

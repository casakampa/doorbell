#!/usr/bin/env python3

import signal
import sys
import logging
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime, time
from pytz import timezone
import paho.mqtt.client as mqtt

### Variables

# Logging
logging.basicConfig(filename='doorbell.log',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# GPIO pins
button_gpio = 24
chime_gpio = 17

# MQTT settings
mqtt_client = "pibell"
mqtt_user = "user"
mqtt_password = "password"
mqtt_address = "192.168.2.1"
mqtt_port = 1883
mqtt_button_topic = "doorbell/button"
mqtt_status_topic = "doorbell/status"
payload_on = "ON"
payload_off = "OFF"
status_online = "online"
status_offline = "offline"

# Time settings
not_before_hour = 6
not_before_minutes = 00
not_after_hour = 23
not_after_minutes = 00
timezone = timezone("Europe/Amsterdam")

### Functions

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now(timezone).time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def shutdown_handler(sig, frame):
    send_offline_status()
    logging.info("State 'offline' is sent to topic")
    sleep(0.5)
    GPIO.cleanup()
    logging.warning("GPIO cleaned up and doorbell will shutdown")
    sys.exit(0)

def send_mqtt_message(topic, payload):
    client = mqtt.Client(mqtt_client)
    client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_address, mqtt_port)
    client.publish(topic, payload, 1, True)
    client.disconnect()

def send_initial_state_message():
    topic = mqtt_button_topic
    payload = payload_off

    send_mqtt_message(topic, payload)

def send_doorbell_message():
    topic = mqtt_button_topic
    payload = payload_on
    send_mqtt_message(topic, payload)
    
    sleep(1)
    
    payload = payload_off
    send_mqtt_message(topic, payload)

def send_online_status():
    topic = mqtt_status_topic
    payload = status_online

    send_mqtt_message(topic, payload)

def send_offline_status():
    topic = mqtt_status_topic
    payload = status_offline

    send_mqtt_message(topic, payload)

def chime():
    GPIO.output(chime_gpio, GPIO.LOW)
    sleep(0.2)
    GPIO.output(chime_gpio, GPIO.HIGH)

def button_pressed(channel):
    if GPIO.input(button_gpio):
       send_doorbell_message()
       if is_time_between( time(not_before_hour,not_before_minutes),
                           time(not_after_hour,not_after_minutes) ):
          chime()
       else:
          logging.warning("Someone rang outside of ring times")

def logic():
    logging.info("Starting doorbell script")

    GPIO.setmode(GPIO.BCM)
    logging.info("Setting GPIO mode to BCM")

    GPIO.setup(button_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    logging.info("Pin 24 is set for doorbell button")

    GPIO.setup(chime_gpio, GPIO.OUT, initial=GPIO.HIGH)
    logging.info("Pin 17 is set for doorbell chime")

    send_online_status()
    logging.info("State 'online' is sent to 'status' topic")

    send_initial_state_message()
    logging.info("State 'off' is sent to 'button' topic")

    GPIO.add_event_detect(button_gpio, GPIO.FALLING,
            callback=button_pressed, bouncetime=100)
    logging.info("Detection of input has started")

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.pause()

if __name__ == '__main__':
    logic()

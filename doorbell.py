#!/usr/bin/env python3

import signal                                                           # Need to find out
import sys                                                              # Need to find out
import logging                                                          # For logging function
import RPi.GPIO as GPIO                                                 # To read the GPIO pins
from time import sleep                                                  # To make something wait for it
from datetime import datetime, time                                     # Needed to do some calculations based on time
from pytz import timezone                                               # Needed to make sure the checked time is according to the right timezone
import paho.mqtt.client as mqtt                                         # For MQTT message sending
import threading                                                        # Threaded? Dunno, maybe it works

### Variables

# Logging
logging.basicConfig(filename='doorbell.log',                            # Log output
                    format='%(asctime)s - %(levelname)s - %(message)s', # Formatting of log entries
                    level=logging.INFO)                                 # Minimal logging level

# GPIO pins
button_gpio = 24                                                        # Input button
chime_gpio = 17                                                         # Output button

# MQTT settings
mqtt_client = "pibell"
mqtt_user = "user"
mqtt_password = "password"
mqtt_broker_address = "192.168.2.1"
mqtt_broker_port = 1883
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

def is_time_between(begin_time, end_time, check_time=None):                                                 # Slightly changed from source: from https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now(timezone).time()                                                # Set the variable
    if begin_time < end_time:                                                                               # Check for condition
        return check_time >= begin_time and check_time <= end_time                                          # Check if begin_time is equal or bigger than begin_time, and check if end_time is equal or lower than end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time                                           # Check if one condition matches

def shutdown_handler(sig, frame):
    send_offline_status()
    logging.info("State 'offline' is sent to topic")
    sleep(0.5)
    GPIO.cleanup()
    logging.warning("GPIO cleaned up and doorbell will shutdown")                                           # Free al the pins
    sys.exit(0)

def send_initial_state_message():
    client = mqtt.Client( mqtt_client )                                                                     # Define a new instance
    client.username_pw_set( mqtt_user, mqtt_password )                                                      # Set the user account
    client.connect( mqtt_broker_address, mqtt_broker_port )                                                 # Connect to the configured broker
    client.publish( mqtt_button_topic, payload_off, 0, True )                                               # Send the second message
    client.disconnect()

def send_doorbell_message():
    client = mqtt.Client( mqtt_client )                                                                     # Define a new instance
    client.username_pw_set( mqtt_user, mqtt_password )                                                      # Set the user account
    client.connect( mqtt_broker_address, mqtt_broker_port )                                                 # Connect to the configured broker
    client.publish( mqtt_button_topic, payload_on, 0, True )                                                # Send the first message
    sleep(1)                                                                                                # Wait for it...
    client.publish( mqtt_button_topic, payload_off, 0, True )                                               # Send the second message
    client.disconnect()                                                                                     # Disconnect from the configured broker

def send_online_status():
    client = mqtt.Client( mqtt_client )                                                                     # Define a new instance
    client.username_pw_set( mqtt_user, mqtt_password )                                                      # Set the user account
    client.connect( mqtt_broker_address, mqtt_broker_port )                                                 # Connect to the configured broker
    client.publish( mqtt_status_topic, status_online, 0, True )                                             # Send the second message
    client.disconnect()

def send_offline_status():
    client = mqtt.Client( mqtt_client )                                                                     # Define a new instance
    client.username_pw_set( mqtt_user, mqtt_password )                                                      # Set the user account
    client.connect( mqtt_broker_address, mqtt_broker_port )                                                 # Connect to the configured broker
    client.publish( mqtt_status_topic, status_offline, 0, True )                                            # Send the second message
    client.disconnect()

def chime():
    GPIO.output(chime_gpio, GPIO.HIGH)                                                                      # Switch relais to activate chime
    sleep(0.2)                                                                                              # Let's make it sound like a doorbell should sound
    GPIO.output(chime_gpio, GPIO.LOW)                                                                       # Switch relais back to deactivate chime

def no_chime():
    GPIO.output(chime_gpio, GPIO.LOW)                                                                       # Make sure the chime is deactivated

def button_pressed(channel):
    if GPIO.input(button_gpio):                                                                             # If input is HIGH
       send_doorbell_message()                                                                              # Activate function send_mqtt_message()
       if is_time_between( time(not_before_hour,not_before_minutes),                                        # Check before time
                           time(not_after_hour,not_after_minutes) ):                                        # Check after time
          chime()                                                                                           # Activate function chime()
       else:
          logging.warning("Someone rang outside of ring times")
    else:
       no_chime()                                                                                           # Activate function no_chime()

def logic():
    logging.info("Starting doorbell script")

    GPIO.setmode(GPIO.BCM)
    logging.info("Setting GPIO mode to BCM")

    GPIO.setup(button_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    logging.info("Pin 24 is set for doorbell button")

    GPIO.setup(chime_gpio, GPIO.OUT, initial=GPIO.LOW)
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

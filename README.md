# Doorbell

The doorbell is installed as a systemd-service. The script itself contains various functions that are [explained](#the-inner-workings-of-the-doorbell-script) below the installation steps. And if you want to build this yourself, take a look at the [hardware](#hardware) section.

## Steps for installation:


1. Become root

	````bash
	sudo -i
	````

2. Download the necessary Python3 packages:

	````bash
	apt install python3-tz python3-rpi.gpio python3-paho-mqtt
	````

3. Create the file doorbell.py file (_I use nano, but you can use the editor you prefer_):

	````bash
	nano /home/user/doorbell/doorbell.py
	````
 
	and add the code from the file ````doorbell.py```` found in this repository.

4. Save the file and exit nano:

	- ````Ctrl + o````
	- ````Enter````
	- ````Ctrl + x````
	- ````Enter````

5. Create the configuration for systemd:

	* Create a new file

		````bash
		nano /etc/systemd/system/doorbell.service
		````

	* Copy the text below into the file:

		````
  		[Unit]
  		Description=Run doorbell.py in /home/user/doorbell/

		[Service]
		ExecStart=/usr/bin/python3 /home/user/doorbell/doorbell.py
		Restart=always
  		User=root

		[Install]
		WantedBy=multi-user.target
		````

	* Save the file and exit nano:

		- ````Ctrl + o````
		- ````Enter````
		- ````Ctrl + x````
		- ````Enter````

	* Make it executable

		````bash
		chmod +x /home/user/doorbell/doorbell.py
		````

6. Update systemd:

	````bash
	service daemon-reload
	````

7. Enable the doorbell service (so it starts when the system restarts):

	````bash
	systemctl enable doorbell.service
	````

8. Start the doorbell service:

	````bash
	systemctl start doorbell.service
	````

If everything went well, your doorbell should ring when you press the doorbell button.

# The inner workings of the doorbell script

The script reads the GPIO pins on the Raspberry Pi. The 3.3V DC power supply is used for the doorbell button. GPIO pin 24 - right next to the 3.3V pin - is used as a sensor to detect power. When someone presses the doorbell button, the circuit closes and GPIO pin 24 detects power.

Then the script checks if someone presses the doorbell button between certain times, and if so, switches a relay - controlled by GPIO pin 17 - to trigger the real doorbell. At the same time, a message is sent to Home Assistant via MQTT to perform [some automations](https://github.com/casakampa/home-assistant-config/blob/master/automations/deurbel.yaml) related to the doorbell.

# Hardware

The following hardware is used to make all this possible:

* Raspberry Pi 2 or higher
* Doorbell push button - the most standard version that can be found online - connected to a 3.3V pin and a GPIO pin (I use GPIO physical pin 17 (3.3V) and 18 (GPIO pin 24) for detection).
* [1 channel relay board](https://www.tinytronics.nl/shop/en/switches/relays/5v-relay-1-channel-high-active-or-low-active) - connected to the [5v power pins](https://pinout.xyz/pinout/pin2_5v_power) of the Raspberry Pi and GPIO pin 17

## Wiring the doorbell

The doorbell wiring is connected to the 1 channel relay as Normally Open (NO). A Normally Open relay will switch to Normally Closed (NC) when the coil is activated. This will result in the circuit being closed and so the doorbell will ring.

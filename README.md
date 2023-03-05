# Doorbell

The doorbell is installed in a virtual environment. The script itself contains various functions that are [explained](#the-inner-workings-of-the-doorbell-script) below the installation steps. And if you want to build this yourself, look at the [hardware](#hardware) section

## Steps for installation:


1. Become root

	````bash
	sudo -i
	````

2. Create a virtual environment:

	````bash
	python3 -m venv /home/user/doorbell/.venv/
	````

3. Open the virtual environment:

	````bash
	source /home/user/doorbell/.venv/bin/activate
	````

	* Install the required Python modules, otherwise the script will give errors:

		````python
		pip3 install rpi.gpio pytz paho-mqtt
		````

	*  Create the file ````doorbell.py```` file (_I use nano, but you can use the editor you prefer_):

		````bash
		nano /home/user/doorbell/doorbell.py
		````

		and add the code from the file ````doorbell.py```` found in this repository.

	* Save the file and exit nano:

		- ````Ctrl + o````
		- ````Enter````
		- ````Ctrl + x````
		- ````Enter````

	* Leave the virtual environment:

		````bash
		exit
		````

8. Become root again:

	````bash
	sudo -i
	````

9. Create the configuration for supervisor:

	* Create a new file

		````bash
		nano /etc/supervisor/conf.d/doorbell.conf
		````

	* Copy the text below into the file:

		````
		[program:doorbell]
		command = /home/user/doorbell/.venv/bin/python3 -m doorbell
		directory = /home/user/doorbell
		autostart=true
		autorestart = true
		startsecs=1
		startretries=10
		stopwaitsecs=30
		redirect_stderr = true
		stdout_logfile = /var/log/doorbell.log
		stderr_logfile = /var/log/doorbell_error.log
		````

	* Save the file and exit nano:

		- ````Ctrl + o````
		- ````Enter````
		- ````Ctrl + x````
		- ````Enter````

	* Update the supervisor:

		````bash
		supervisorctl reread
		supervisorctl update
		supervisorctl status
		````

If everything went well, your doorbell should ring when you press the doorbell button.

# The inner workings of the doorbell script

The script reads the GPIO pins on the Raspberry Pi. The 3.3V DC power supply is used for the doorbell button. GPIO pin 24 - right next to the 3.3V pin - is used as a sensor to detect power. When someone presses the doorbell button, the circuit closes and GPIO pin 24 detects power.

Then the script checks if someone presses the doorbell button between certain times, and if so, switches a relay - controlled by GPIO pin 17 - to trigger the real doorbell. At the same time, a message is sent to Home Assistant via MQTT to perform [some automations](https://github.com/mvandek/home-assistant-config/blob/master/automations/deurbel.yaml) related to the doorbell.

# Hardware

The following hardware is used to make all this possible:

* Raspberry Pi 3 Model B
* Doorbell button - the most standard version that can be found online
* 1 channel relay board - connected to the [5v power pins](https://pinout.xyz/pinout/pin2_5v_power) of the Raspberry Pi

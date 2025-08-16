# Venus OS DBus-MQTT Inverter

This script integrates MQTT data into Venus OS as a standalone inverter or PV inverter via DBus.

## Features
- Supports "inverter" and "pvinverter" modes via config.
- Initializes as "off" / zero values.
- Configurable MQTT settings (host, port, auth, topic).
- Production-ready with optional debug logging (--debug).

## Requirements
- Venus OS device (e.g., Cerbo GX).
- MQTT broker (Venus OS or external).
- config.ini in the same directory.

## Installation
1. Copy the script to `/data/venus-custom/inverter/dbus-mqtt-inverter.py`.
2. Create config.ini from config.sample.ini and edit:
   ```ini
   [DEFAULT]
   device_instance = 111
   device_type = inverter  # or pvinverter
   mqtt_host = localhost
   mqtt_port = 1883
   mqtt_user = 
   mqtt_password = 
   mqtt_topic = inverter
   debug = False

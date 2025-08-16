# Venus OS DBus-MQTT Inverter

This script integrates MQTT data into Venus OS as a standalone inverter or PV inverter via DBus.  
**Last updated:** 08:56 PM EDT, Friday, August 15, 2025.

## Features
- Supports "inverter" and "pvinverter" modes via config.
- Initializes as "off"/zero values.
- Configurable MQTT settings, mode (1-4), and number of phases (1-3).
- Optional L2/L3 output support for multi-phase systems.
- Production-ready with optional debug logging (`--debug`).
- Based on Victron's VeDbusService and mr-manuel's dbus-mqtt-grid.py.

## Requirements
- Venus OS device (e.g., Cerbo GX, v3.x or later).
- MQTT broker (Venus OS or external).
- Python 3 with dependencies:
  - `vedbus` and `ve_utils` (pre-installed in `/opt/victronenergy/dbus-systemcalc-py/ext/velib_python/`).
  - `paho.mqtt.client` (install with `opkg install python3-paho-mqtt`).
  - `gi.repository.GLib` (install with `opkg install python3-gi` if missing).
- Verify with: `python3 -c "import vedbus, ve_utils, paho.mqtt.client, gi.repository.GLib"`.

## Installation
1. Copy the script to `/data/venus-custom/inverter/dbus-mqtt-inverter.py`.
2. Create `config.ini` from `config.sample.ini` and edit:
   ```ini
   [DEFAULT]
   device_instance = 111
   device_type = inverter  # or pvinverter
   mode = 4              # 1=Charger Only, 2=Inverter Only, 3=On, 4=Off
   num_phases = 1        # 1, 2, or 3 phases

   [MQTT]
   host = localhost
   port = 1883
   user =
   password =
   topic = inverter
   debug = False

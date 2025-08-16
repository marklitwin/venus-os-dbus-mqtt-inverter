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
3. Install dependencies (if needed):
        bashopkg update
        opkg install python3-paho-mqtt python3-gi
4.  Run: sudo python3 /data/venus-custom/inverter/dbus-mqtt-inverter.py
    For boot startup, add to /data/rc.local or use a service (recommended).

## MQTT Payload Example
```ini
{
  "state": 8,
  "power": 20.0,
  "voltage": 120.5,
  "frequency": 60.0,
  "load": 37.5,
  "connected": 1,
  "error": 0,
  "dc_voltage": 13.2,
  "dc_current": 0.0,
  "temperature": 42.0,
  "L2_voltage": 120.5,    # Optional L2 output voltage (for 2+ phases)
  "L2_load": 35.0,        # Optional L2 current
  "L2_power": 18.0,       # Optional L2 power
  "L2_frequency": 60.0,   # Optional L2 frequency
  "L3_voltage": 120.5,    # Optional L3 output voltage (for 3 phases)
  "L3_load": 34.0,        # Optional L3 current
  "L3_power": 17.0,       # Optional L3 power
  "L3_frequency": 60.0    # Optional L3 frequency
}
````

L1 fields (voltage, load, power, frequency) are required.
L2/L3 fields are optional and processed if num_phases is 2 or 3.

## Mode Options (/Mode)

1 = Charger Only
2 = Inverter Only
3 = On
4 = Off (default)
See CCGX manual for limitations.

## Debug
Run with --debug or set debug = True in config.ini.

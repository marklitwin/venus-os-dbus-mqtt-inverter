#!/usr/bin/env python3

# dbus-mqtt-inverter.py - Integrates MQTT data into Venus OS as a standalone or PV inverter via DBus.
# Supports configurable device type (inverter/pvinverter), number of phases, and initializes as "off"/zero.
# Based on Victron's VeDbusService and mr-manuel's dbus-mqtt-grid.py.
# Usage: sudo python3 dbus-mqtt-inverter.py [--debug]
# Config: /data/venus-custom/inverter/config.ini
# MQTT Topic: rv/<mqtt_topic>/status
# GitHub: Publish with this script and config.sample.ini.

import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import paho.mqtt.client as mqtt
import json
import configparser
import os
import logging
import argparse
from vedbus import VeDbusService
from ve_utils import get_vrm_portal_id

def get_text(value, path):
    """Format Text values with units for GUI display."""
    if path in ["/Ac/Out/L1/V", "/Ac/L1/Voltage", "/Ac/Out/L2/V", "/Ac/Out/L3/V"]:
        return f"{value:.1f} V"
    elif path in ["/Ac/Out/L1/I", "/Ac/L1/Current", "/Ac/Out/L2/I", "/Ac/Out/L3/I"]:
        return f"{value:.2f} A"
    elif path in ["/Ac/Out/L1/P", "/Ac/L1/Power", "/Ac/Power", "/Ac/Out/L2/P", "/Ac/Out/L3/P"]:
        return f"{value:.1f} W"
    elif path in ["/Ac/Out/L1/F", "/Ac/L1/Frequency", "/Ac/Out/L2/F", "/Ac/Out/L3/F"]:
        return f"{value:.1f} Hz"
    elif path == "/Dc/0/Voltage":
        return f"{value:.1f} V"
    elif path == "/Dc/0/Current":
        return f"{value:.1f} A"
    elif path == "/Dc/0/Temperature":
        return f"{value:.1f} °C"
    elif path in ["/DeviceInstance", "/Connected", "/State", "/Mode", "/Error", "/Position", "/Ac/Out/NumberOfPhases"]:
        return str(value)
    elif path in ["/ProductId", "/DeviceType"]:
        return f"0x{value:X}"
    elif path == "/Ac/Energy/Forward":
        return f"{value:.1f} kWh"
    return str(value)

def main():
    # Parse --debug flag
    parser = argparse.ArgumentParser(description="DBus-MQTT Inverter Service")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging
    config = configparser.ConfigParser()
    config.read("/data/venus-custom/inverter/config.ini")
    debug_config = config["MQTT"].getboolean("debug", False)
    debug_level = logging.DEBUG if args.debug or debug_config else logging.INFO
    logging.basicConfig(level=debug_level)
    logger = logging.getLogger(__name__)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Load configuration
    device_instance = int(config["DEFAULT"].get("device_instance", "111"))
    device_type = config["DEFAULT"].get("device_type", "inverter")
    if device_type not in ["inverter", "pvinverter"]:
        logger.error("Invalid device_type. Use 'inverter' or 'pvinverter'.")
        return
    mode = int(config["DEFAULT"].get("mode", "4"))  # 1-4
    num_phases = int(config["DEFAULT"].get("num_phases", "1"))  # 1, 2, or 3
    if num_phases not in [1, 2, 3]:
        logger.error("Invalid num_phases. Use 1, 2, or 3.")
        num_phases = 1

    mqtt = config["MQTT"]
    host = mqtt.get("host", "localhost")
    port = int(mqtt.get("port", "1883"))
    user = mqtt.get("user", "")
    password = mqtt.get("password", "")
    topic = mqtt.get("topic", "inverter")

    service_name = f"com.victronenergy.{device_type}.mqtt_{device_instance}"
    connection = "BLE → MQTT → dbus"

    # Initialize VeDbusService with register=False
    dbusservice = VeDbusService(service_name, bus=dbus.SystemBus(), register=False)

    # Add common paths
    dbusservice.add_path('/DeviceInstance', device_instance, gettextcallback=get_text)
    dbusservice.add_path('/ProductName', 'MQTT Inverter', gettextcallback=get_text)
    dbusservice.add_path('/Connected', 1, gettextcallback=get_text)
    dbusservice.add_path('/FirmwareVersion', 'v1.0', gettextcallback=get_text)
    dbusservice.add_path('/ProductId', 0xA381, gettextcallback=get_text)
    dbusservice.add_path('/DeviceType', 0x203, gettextcallback=get_text)
    dbusservice.add_path('/Serial', 'MQTT123456', gettextcallback=get_text)
    dbusservice.add_path('/HardwareVersion', '1.0', gettextcallback=get_text)
    dbusservice.add_path('/CustomName', '', gettextcallback=get_text)
    dbusservice.add_path('/Mgmt/ProcessName', 'dbus-mqtt-inverter.py', gettextcallback=get_text)
    dbusservice.add_path('/Mgmt/Connection', connection, gettextcallback=get_text)
    dbusservice.add_path('/Error', 0, gettextcallback=get_text)

    # Add type-specific paths with initial zero/off values
    if device_type == "inverter":
        dbusservice.add_path('/State', 0, gettextcallback=get_text)  # 0 = Off
        dbusservice.add_path('/Ac/Out/NumberOfPhases', num_phases, gettextcallback=get_text)
        dbusservice.add_path('/Ac/ActiveIn/Connected', 0, gettextcallback=get_text)
        dbusservice.add_path('/Ac/Out/L1/V', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Ac/Out/L1/I', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Ac/Out/L1/P', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Ac/Out/L1/F', 0.0, gettextcallback=get_text)
        if num_phases >= 2:
            dbusservice.add_path('/Ac/Out/L2/V', 0.0, gettextcallback=get_text)
            dbusservice.add_path('/Ac/Out/L2/I', 0.0, gettextcallback=get_text)
            dbusservice.add_path('/Ac/Out/L2/P', 0.0, gettextcallback=get_text)
            dbusservice.add_path('/Ac/Out/L2/F', 0.0, gettextcallback=get_text)
        if num_phases == 3:
            dbusservice.add_path('/Ac/Out/L3/V', 0.0, gettextcallback=get_text)
            dbusservice.add_path('/Ac/Out/L3/I', 0.0, gettextcallback=get_text)
            dbusservice.add_path('/Ac/Out/L3/P', 0.0, gettextcallback=get_text)
            dbusservice.add_path('/Ac/Out/L3/F', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Dc/0/Voltage', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Dc/0/Current', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Dc/0/Temperature', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Mode', mode, gettextcallback=get_text, writeable=True)
    else:  # pvinverter
        dbusservice.add_path('/State', 0, gettextcallback=get_text)  # 0 = Off
        dbusservice.add_path('/Position', 0, gettextcallback=get_text)  # 0 = AC output
        dbusservice.add_path('/Ac/L1/Voltage', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Ac/L1/Current', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Ac/Power', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Ac/L1/Frequency', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Ac/Energy/Forward', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Dc/0/Voltage', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Dc/0/Current', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Dc/0/Temperature', 0.0, gettextcallback=get_text)
        dbusservice.add_path('/Mode', 3, gettextcallback=get_text, writeable=True)

    # Register the service
    dbusservice.register()

    logger.info(f"Registered service: {service_name}")

    def on_connect(client, userdata, flags, rc, properties=None):
        logger.info(f"MQTT connected with result code {rc}")
        client.subscribe(f"rv/{topic}/status")

    def on_disconnect(client, userdata, rc):
        logger.info(f"MQTT disconnected with result code {rc}")

    def on_message(client, userdata, msg):
        logger.debug(f"MQTT message received: {msg.topic} {msg.payload}")
        try:
            data = json.loads(msg.payload)
            if "state" in data:
                dbusservice['/State'] = data["state"]
            if "voltage" in data:
                if device_type == "inverter":
                    dbusservice['/Ac/Out/L1/V'] = data["voltage"]
                else:
                    dbusservice['/Ac/L1/Voltage'] = data["voltage"]
            if "L2_voltage" in data and device_type == "inverter" and num_phases >= 2:
                dbusservice['/Ac/Out/L2/V'] = data["L2_voltage"]
            if "L3_voltage" in data and device_type == "inverter" and num_phases == 3:
                dbusservice['/Ac/Out/L3/V'] = data["L3_voltage"]
            if "load" in data:
                if device_type == "inverter":
                    dbusservice['/Ac/Out/L1/I'] = data["load"]
                else:
                    dbusservice['/Ac/L1/Current'] = data["load"]
            if "L2_load" in data and device_type == "inverter" and num_phases >= 2:
                dbusservice['/Ac/Out/L2/I'] = data["L2_load"]
            if "L3_load" in data and device_type == "inverter" and num_phases == 3:
                dbusservice['/Ac/Out/L3/I'] = data["L3_load"]
            if "power" in data:
                if device_type == "inverter":
                    dbusservice['/Ac/Out/L1/P'] = data["power"]
                else:
                    dbusservice['/Ac/Power'] = data["power"]
            if "L2_power" in data and device_type == "inverter" and num_phases >= 2:
                dbusservice['/Ac/Out/L2/P'] = data["L2_power"]
            if "L3_power" in data and device_type == "inverter" and num_phases == 3:
                dbusservice['/Ac/Out/L3/P'] = data["L3_power"]
            if "frequency" in data:
                if device_type == "inverter":
                    dbusservice['/Ac/Out/L1/F'] = data["frequency"]
                else:
                    dbusservice['/Ac/L1/Frequency'] = data["frequency"]
            if "L2_frequency" in data and device_type == "inverter" and num_phases >= 2:
                dbusservice['/Ac/Out/L2/F'] = data["L2_frequency"]
            if "L3_frequency" in data and device_type == "inverter" and num_phases == 3:
                dbusservice['/Ac/Out/L3/F'] = data["L3_frequency"]
            if "dc_voltage" in data:
                dbusservice['/Dc/0/Voltage'] = data["dc_voltage"]
            if "dc_current" in data:
                dbusservice['/Dc/0/Current'] = data["dc_current"]
            if "temperature" in data:
                dbusservice['/Dc/0/Temperature'] = data["temperature"]
            if "connected" in data:
                dbusservice['/Connected'] = data["connected"]
            if "mode" in data:
                dbusservice['/Mode'] = data["mode"]
            if "error" in data:
                dbusservice['/Error'] = data["error"]
        except Exception as e:
            logger.error(f"MQTT payload error: {e}")

    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                         client_id="MqttInverter_" + get_vrm_portal_id() + "_" + str(device_instance))
    if user and password:
        client.username_pw_set(user, password)
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port, 60)
    client.loop_start()

    GLib.MainLoop().run()

if __name__ == "__main__":
    main()

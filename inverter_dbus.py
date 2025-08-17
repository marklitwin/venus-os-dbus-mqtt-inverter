import dbus
import dbus.mainloop.glib
from gi.repository import GLib
from vedbus import VeDbusService
import logging

def setup_dbus_service(device_instance, num_phases, device_name, serial_number, mode, logger):
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    service_name = f"com.victronenergy.inverter.mqtt_{device_instance}"
    connection = "BLE → MQTT → dbus"
    dbusservice = VeDbusService(service_name, bus=dbus.SystemBus(), register=False)

    path_values = {}
    paths = []

    def handle_dbus_write(path, value):
        logger.debug(f"DBus write request: {path} = {value}")
        if path in ["/State", "/Mode"]:
            path_values[path] = value
            dbusservice[path] = value
            logger.info(f"Updated {path} to {value}")
            return True
        return False

    def add_path(path, value, writeable=False, onchangecallback=None):
        dbusservice.add_path(path, value, gettextcallback=get_text, writeable=writeable, onchangecallback=onchangecallback)
        path_values[path] = value
        paths.append(path)
        logger.debug(f"Added {path} with start value {value}. Writeable is {writeable}")

    def get_text(value, path):
        try:
            if path in ["/DeviceInstance", "/Connected", "/State", "/Mode", "/Error", "/Ac/Out/NumberOfPhases", "/IsReconfigurable", "/Ac/ActiveIn/ActiveInput",
                        "/Alarms/GridLost", "/Alarms/HighTemperature", "/Alarms/LowBattery", "/Alarms/Overload",
                        "/Alarms/Ripple", "/Alarms/TemperatureSensor", "/Alarms/VoltageSensor",
                        "/Bms/AllowToCharge", "/Bms/AllowToDischarge", "/Bms/BmsExpected", "/Bms/Error",
                        "/Leds/Mains", "/Leds/Bulk", "/Leds/Absorption", "/Leds/Float", "/Leds/Inverter",
                        "/Leds/Overload", "/Leds/LowBattery", "/Leds/Temperature"]:
                return str(value)
            elif path in ["/ProductId", "/DeviceType"]:
                return f"0x{value:X}"
            elif path in ["/CustomName", "/Serial", "/FirmwareVersion2", "/Mgmt/ProcessName", "/Mgmt/Connection"]:
                return str(value)
            elif path in ["/Ac/Out/L1/V", "/Ac/Out/L2/V", "/Ac/Out/L3/V"]:
                return f"{float(value):.1f} V"
            elif path in ["/Ac/Out/L1/I", "/Ac/Out/L2/I", "/Ac/Out/L3/I"]:
                return f"{float(value):.2f} A"
            elif path in ["/Ac/Out/L1/P", "/Ac/Out/L2/P", "/Ac/Out/L3/P", "/Dc/0/Power"]:
                return f"{float(value):.1f} W"
            elif path in ["/Ac/Out/L1/S", "/Ac/Out/L2/S", "/Ac/Out/L3/S"]:
                return f"{float(value):.1f} VA"
            elif path in ["/Ac/Out/L1/F", "/Ac/Out/L2/F", "/Ac/Out/L3/F"]:
                return f"{float(value):.1f} Hz"
            elif path == "/Dc/0/Voltage":
                return f"{float(value):.1f} V"
            elif path == "/Dc/0/Current":
                return f"{float(value):.1f} A"
            elif path == "/Dc/0/Temperature":
                return f"{float(value):.1f} °C"
            else:
                return str(value)
        except (TypeError, ValueError) as e:
            logging.debug(f"get_text error for path {path} with value {value}: {e}")
            return str(value)

    # Add common paths
    add_path('/DeviceInstance', device_instance)
    add_path('/ProductName', 'MQTT Inverter')
    add_path('/Connected', 1)
    add_path('/FirmwareVersion', 'v1.0')
    add_path('/FirmwareVersion2', 'v1.0')
    add_path('/ProductId', 0xA381)
    add_path('/DeviceType', 0x203)
    add_path('/Serial', serial_number)
    add_path('/CustomName', device_name)
    add_path('/Mgmt/ProcessName', 'dbus-mqtt-inverter.py')
    add_path('/Mgmt/Connection', connection)
    add_path('/Error', 0)
    add_path('/IsReconfigurable', 0)

    # Add inverter-specific paths
    add_path('/State', 0, writeable=True, onchangecallback=handle_dbus_write)
    add_path('/Mode', mode, writeable=True, onchangecallback=handle_dbus_write)
    add_path('/Ac/Out/NumberOfPhases', num_phases)
    add_path('/Ac/ActiveIn/Connected', 0)
    add_path('/Ac/ActiveIn/ActiveInput', 240)  # 0=ACin-1, 1=ACin-2, 240=none/inverting
    add_path('/Ac/Out/L1/V', 0.0)
    add_path('/Ac/Out/L1/I', 0.0)
    add_path('/Ac/Out/L1/P', 0.0)
    add_path('/Ac/Out/L1/F', 0.0)
    add_path('/Ac/Out/L1/S', 0.0)
    if num_phases >= 2:
        add_path('/Ac/Out/L2/V', 0.0)
        add_path('/Ac/Out/L2/I', 0.0)
        add_path('/Ac/Out/L2/P', 0.0)
        add_path('/Ac/Out/L2/F', 0.0)
        add_path('/Ac/Out/L2/S', 0.0)
    if num_phases == 3:
        add_path('/Ac/Out/L3/V', 0.0)
        add_path('/Ac/Out/L3/I', 0.0)
        add_path('/Ac/Out/L3/P', 0.0)
        add_path('/Ac/Out/L3/F', 0.0)
        add_path('/Ac/Out/L3/S', 0.0)
    add_path('/Dc/0/Voltage', 0.0)
    add_path('/Dc/0/Current', 0.0)
    add_path('/Dc/0/Power', 0.0)
    add_path('/Dc/0/Temperature', 0.0)
    add_path('/Alarms/GridLost', 0)
    add_path('/Alarms/HighTemperature', 0)
    add_path('/Alarms/LowBattery', 0)
    add_path('/Alarms/Overload', 0)
    add_path('/Alarms/Ripple', 0)
    add_path('/Alarms/TemperatureSensor', 0)
    add_path('/Alarms/VoltageSensor', 0)
    add_path('/Bms/AllowToCharge', 0)
    add_path('/Bms/AllowToDischarge', 0)
    add_path('/Bms/BmsExpected', 0)
    add_path('/Bms/Error', 0)
    add_path('/Leds/Mains', 0)
    add_path('/Leds/Bulk', 0)
    add_path('/Leds/Absorption', 0)
    add_path('/Leds/Float', 0)
    add_path('/Leds/Inverter', 0)
    add_path('/Leds/Overload', 0)
    add_path('/Leds/LowBattery', 0)
    add_path('/Leds/Temperature', 0)

    dbusservice.register()
    logger.info(f"Registered service: {service_name}")
    return dbusservice, path_values

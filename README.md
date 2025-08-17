# venus-os-dbus-mqtt-inverter

A Python script to integrate an MQTT-based inverter into the Victron Venus OS ecosystem via DBus, allowing it to be displayed and managed in the Cerbo GX user interface. This modular implementation subscribes to an MQTT topic, processes JSON payloads, and updates DBus paths accordingly.

## Features
- Supports configurable device instance, number of phases, device name, serial number, and mode.
- Handles MQTT messages and maps them to Victron-compatible DBus paths for inverters.
- Modular design with separate files for configuration, DBus service, MQTT handling, and main execution.
- Compatible with Venus OS environment (e.g., Cerbo GX).

## Prerequisites
- Venus OS environment (e.g., Cerbo GX).
- MQTT broker (e.g., Mosquitto) running and accessible.
- Python 3 with required libraries: paho-mqtt, dbus, gi, vedbus, ve_utils (typically pre-installed on Venus OS).

## Installation

1. Clone the Repository
   Use the command git clone https://github.com/marklitwin/venus-os-dbus-mqtt-inverter.git followed by cd venus-os-dbus-mqtt-inverter.
   ```bash
   git clone https://github.com/your-username/dbus-mqtt-inverter.git
   cd dbus-mqtt-inverter
   ````

3. Configure the Project
   - Copy the config.ini.example to config.ini and edit it with your settings:
     Under DEFAULT section, set device_instance, num_phases, device_name, serial_number, and mode (1 for Charger Only, 2 for Inverter Only, 3 for On, 4 for Off).
     Under MQTT section, set host, port, user, password, topic (your MQTT topic), and debug (true or false).
   - Adjust device_instance to avoid conflicts with existing devices (check with dbus -y | grep inverter).
   - Set topic to match your MQTT publisher's topic.

4. Set Permissions
   Use chmod +x *.py to make the scripts executable.
   ```bash
   chmod +x *.py
   ````

5. Run the Script
   Use sudo python3 inverter_main.py --debug to start the script with debug logging.
   ```bash
   sudo python3 inverter_main.py --debug
   ````

## Usage
- Publish JSON payloads to the MQTT topic specified in config.ini (default is inverter).
- The script registers a DBus service (com.victronenergy.inverter.mqtt_ followed by your device_instance) and updates the Cerbo GX UI with inverter status, power output, and other metrics.
- Use --debug for detailed logging to troubleshoot issues.

## JSON Payload Examples

### Minimal JSON Payload
This is the simplest payload to make the inverter appear in the Cerbo GX UI with basic status and power output. It includes State set to 9 for Inverting, Connected set to 1, and Ac with Out and L1 containing P set to 20.0 for 20 watts of power output.
```json
{
  "State": 9,        // Inverting (see Victron state codes)
  "Connected": 1,    // Device is connected
  "Ac": {
    "Out": {
      "L1": {
        "P": 20.0     // Power output in watts (float recommended)
      }
    }
  }
}
````


### Full JSON Payload
This includes all supported fields for comprehensive inverter data. It covers State, Mode, Connected, CustomName, Serial, Error, FirmwareVersion2, IsReconfigurable, Ac with ActiveIn and Out details (including voltage, current, power, frequency, and apparent power for L1, L2, and L3), Dc with voltage, current, power, and temperature, Alarms, Bms, and Leds. Adjust values like voltages and currents to match your inverter's specifications. The ActiveInput field can be 0 for ACin-1 (Grid), 1 for ACin-2 (Genset), or 240 for Inverting/No Input.
```json
{
  "State": 9,        // Inverting (0=Off, 1=Low Power, 2=Fault, 3=Bulk, 4=Absorption, 5=Float, 9=Inverting)
  "Mode": 3,         // On (1=Charger Only, 2=Inverter Only, 3=On, 4=Off)
  "Connected": 1,    // Device is connected
  "CustomName": "My Inverter",
  "Serial": "INV123456789",
  "Error": 0,        // No error
  "FirmwareVersion2": "v1.0",
  "IsReconfigurable": 0,
  "Ac": {
    "ActiveIn": {
      "ActiveInput": 1  // 0=ACin-1 (Grid), 1=ACin-2 (Genset), 240=Inverting/No Input
    },
    "Out": {
      "L1": {
        "V": 230.0,    // Voltage in volts
        "I": 0.09,     // Current in amps
        "P": 20.0,     // Power in watts
        "F": 50.0,     // Frequency in Hz
        "S": 20.0      // Apparent power in VA
      },
      "L2": {
        "V": 230.0,
        "I": 0.09,
        "P": 20.0,
        "F": 50.0,
        "S": 20.0
      },
      "L3": {
        "V": 230.0,
        "I": 0.09,
        "P": 20.0,
        "F": 50.0,
        "S": 20.0
      }
    }
  },
  "Dc": {
    "0": {
      "Voltage": 48.0,   // DC voltage in volts
      "Current": 0.5,    // DC current in amps
      "Power": 24.0,     // DC power in watts
      "Temperature": 25.0 // Temperature in °C
    }
  },
  "Alarms": {
    "GridLost": 0,
    "HighTemperature": 0,
    "LowBattery": 0,
    "Overload": 0,
    "Ripple": 0,
    "TemperatureSensor": 0,
    "VoltageSensor": 0
  },
  "Bms": {
    "AllowToCharge": 0,
    "AllowToDischarge": 0,
    "BmsExpected": 0,
    "Error": 0
  },
  "Leds": {
    "Mains": 0,
    "Bulk": 0,
    "Absorption": 0,
    "Float": 0,
    "Inverter": 1,
    "Overload": 0,
    "LowBattery": 0,
    "Temperature": 0
  }
}
````


## Troubleshooting
- Device Not Showing: Check device_instance for conflicts and ensure Connected and State are set.
- MQTT Errors: Verify the broker is reachable and the topic matches config.ini.
- Debug Logs: Run with --debug and review logs for errors.

## Contributing
Feel free to submit issues or pull requests on GitHub. Contributions to add support for other device types or enhance functionality are welcome!

## License
MIT License (or specify your preferred license).

## Acknowledgements
- Based on Victron's VeDbusService and inspired by mr-manuel's dbus-mqtt-grid.py.
- Thanks to the xAI community for support in development!

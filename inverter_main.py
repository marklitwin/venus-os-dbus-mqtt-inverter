import logging
import argparse
from inverter_config import load_config
from inverter_dbus import setup_dbus_service
from inverter_mqtt import setup_mqtt_client
from gi.repository import GLib

def main():
    # Parse --debug flag
    parser = argparse.ArgumentParser(description="DBus-MQTT Inverter Service")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging
    config = load_config()
    debug_level = logging.DEBUG if args.debug or config["debug"] else logging.INFO
    logging.basicConfig(level=debug_level)
    logger = logging.getLogger(__name__)

    # Setup DBus service
    dbusservice, path_values = setup_dbus_service(
        config["device_instance"],
        config["num_phases"],
        config["device_name"],
        config["serial_number"],
        config["mode"],
        logger
    )

    # Setup MQTT client
    client = setup_mqtt_client(
        config["mqtt_host"],
        config["mqtt_port"],
        config["mqtt_user"],
        config["mqtt_password"],
        config["mqtt_topic"],
        dbusservice,
        path_values
    )

    GLib.MainLoop().run()

if __name__ == "__main__":
    main()

import configparser
import logging
import os

def load_config():
    config = configparser.ConfigParser()
    config.read("/data/venus-custom/inverter/config.ini")
    logger = logging.getLogger(__name__)
    
    if not config:
        logger.error("Failed to load config.ini")
        raise FileNotFoundError("config.ini not found or empty")

    # Default values
    device_instance = int(config["DEFAULT"].get("device_instance", "111"))
    num_phases = int(config["DEFAULT"].get("num_phases", "1"))
    if num_phases not in [1, 2, 3]:
        logger.error("Invalid num_phases. Use 1, 2, or 3. Defaulting to 1.")
        num_phases = 1
    device_name = config["DEFAULT"].get("device_name", "")
    serial_number = config["DEFAULT"].get("serial_number", "MQTT123456")
    mode = int(config["DEFAULT"].get("mode", "4"))  # 1=Charger Only, 2=Inverter Only, 3=On, 4=Off

    mqtt_config = config["MQTT"]
    host = mqtt_config.get("host", "localhost")
    port = int(mqtt_config.get("port", "1883"))
    user = mqtt_config.get("user", "")
    password = mqtt_config.get("password", "")
    topic = mqtt_config.get("topic", "inverter")
    debug_config = mqtt_config.getboolean("debug", False)

    return {
        "device_instance": device_instance,
        "num_phases": num_phases,
        "device_name": device_name,
        "serial_number": serial_number,
        "mode": mode,
        "mqtt_host": host,
        "mqtt_port": port,
        "mqtt_user": user,
        "mqtt_password": password,
        "mqtt_topic": topic,
        "debug": debug_config
    }

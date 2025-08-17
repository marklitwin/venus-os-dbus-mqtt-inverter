import paho.mqtt.client as mqtt_client
import logging
import json
from ve_utils import get_vrm_portal_id

def setup_mqtt_client(host, port, user, password, topic, dbusservice, path_values):
    logger = logging.getLogger(__name__)
    client = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
                               client_id="MqttInverter_" + get_vrm_portal_id() + "_" + str(path_values['/DeviceInstance']))

    if user and password:
        client.username_pw_set(user, password)

    def on_connect(client, userdata, flags, rc, properties=None):
        logger.info(f"MQTT connected with result code {rc}")
        subscribed_topic = topic
        logger.info(f"Subscribing to topic: {subscribed_topic}")
        client.subscribe(subscribed_topic)

    def on_disconnect(client, userdata, rc):
        logger.info(f"MQTT disconnected with result code {rc}")

    def on_message(client, userdata, msg):
        logger.debug(f"MQTT message received on topic: {msg.topic} with payload: {msg.payload}")
        try:
            data = json.loads(msg.payload)
        except Exception as e:
            logger.error(f"Failed to parse MQTT payload: {e}")
            return

        def update_path(path, value):
            try:
                if value is not None:
                    path_values[path] = value
                    dbusservice[path] = value
                    logger.debug(f"Pushing to DBus: {path} = {value}")
            except Exception as e:
                logger.error(f"Error updating {path} with value {value}: {e}")

        # Common root-level updates
        update_path('/State', data.get("State"))
        update_path('/Mode', data.get("Mode"))
        update_path('/Connected', data.get("Connected"))
        update_path('/CustomName', data.get("CustomName"))
        update_path('/Serial', data.get("Serial"))
        update_path('/Error', data.get("Error"))
        update_path('/FirmwareVersion2', data.get("FirmwareVersion2"))
        update_path('/IsReconfigurable', data.get("IsReconfigurable"))

        # AC ActiveIn updates
        ac_active_in = data.get("Ac", {}).get("ActiveIn", {})
        update_path('/Ac/ActiveIn/ActiveInput', ac_active_in.get("ActiveInput"))

        # AC Out updates
        ac_out = data.get("Ac", {}).get("Out", {})
        l1 = ac_out.get("L1", {})
        update_path('/Ac/Out/L1/V', l1.get("V"))
        update_path('/Ac/Out/L1/I', l1.get("I"))
        update_path('/Ac/Out/L1/P', l1.get("P"))
        update_path('/Ac/Out/L1/F', l1.get("F"))
        update_path('/Ac/Out/L1/S', l1.get("S"))

        if path_values['/Ac/Out/NumberOfPhases'] >= 2:  # Changed from dbusservice.get_path
            l2 = ac_out.get("L2", {})
            update_path('/Ac/Out/L2/V', l2.get("V"))
            update_path('/Ac/Out/L2/I', l2.get("I"))
            update_path('/Ac/Out/L2/P', l2.get("P"))
            update_path('/Ac/Out/L2/F', l2.get("F"))
            update_path('/Ac/Out/L2/S', l2.get("S"))

        if path_values['/Ac/Out/NumberOfPhases'] == 3:  # Changed from dbusservice.get_path
            l3 = ac_out.get("L3", {})
            update_path('/Ac/Out/L3/V', l3.get("V"))
            update_path('/Ac/Out/L3/I', l3.get("I"))
            update_path('/Ac/Out/L3/P', l3.get("P"))
            update_path('/Ac/Out/L3/F', l3.get("F"))
            update_path('/Ac/Out/L3/S', l3.get("S"))

        # DC updates
        dc_0 = data.get("Dc", {}).get("0", {})
        update_path('/Dc/0/Voltage', dc_0.get("Voltage"))
        update_path('/Dc/0/Current', dc_0.get("Current"))
        update_path('/Dc/0/Power', dc_0.get("Power"))
        update_path('/Dc/0/Temperature', dc_0.get("Temperature"))

        # Alarms updates
        alarms = data.get("Alarms", {})
        update_path('/Alarms/GridLost', alarms.get("GridLost"))
        update_path('/Alarms/HighTemperature', alarms.get("HighTemperature"))
        update_path('/Alarms/LowBattery', alarms.get("LowBattery"))
        update_path('/Alarms/Overload', alarms.get("Overload"))
        update_path('/Alarms/Ripple', alarms.get("Ripple"))
        update_path('/Alarms/TemperatureSensor', alarms.get("TemperatureSensor"))
        update_path('/Alarms/VoltageSensor', alarms.get("VoltageSensor"))

        # BMS updates
        bms = data.get("Bms", {})
        update_path('/Bms/AllowToCharge', bms.get("AllowToCharge"))
        update_path('/Bms/AllowToDischarge', bms.get("AllowToDischarge"))
        update_path('/Bms/BmsExpected', bms.get("BmsExpected"))
        update_path('/Bms/Error', bms.get("Error"))

        # Leds updates
        leds = data.get("Leds", {})
        update_path('/Leds/Mains', leds.get("Mains"))
        update_path('/Leds/Bulk', leds.get("Bulk"))
        update_path('/Leds/Absorption', leds.get("Absorption"))
        update_path('/Leds/Float', leds.get("Float"))
        update_path('/Leds/Inverter', leds.get("Inverter"))
        update_path('/Leds/Overload', leds.get("Overload"))
        update_path('/Leds/LowBattery', leds.get("LowBattery"))
        update_path('/Leds/Temperature', leds.get("Temperature"))

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    logger.info(f"Attempting to connect to MQTT broker at {host}:{port}")
    client.connect(host, port, 60)
    client.loop_start()
    return client

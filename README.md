# venus-os-dbus-mqtt-inverter
Integrate MQTT data into Venus OS as a standalone inverter or PV inverter via DBus. Configurable with config.ini for device instance, type (inverter/pvinverter), MQTT host/port/auth/topic, and debug. Initializes as "off"/zero, supports modes (1=Charger Only, 2=Inverter Only, 3=On, 4=Off), and publishes to GUI/MQTT N/ node. Based mr-manuel's work.

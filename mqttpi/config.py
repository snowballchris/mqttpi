import os


# MQTT broker configuration (can be overridden by environment variables)
MQTT_BROKER = os.getenv("MQTT_BROKER", "homeassistant.local")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "mqtt-user-hon")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "passwd-mqtt-user-hon")

# MQTT topics for commands and state
CMD_DISPLAY = os.getenv("CMD_DISPLAY", "pi/display/command")
STATE_DISPLAY = os.getenv("STATE_DISPLAY", "pi/display/state")
CMD_URL = os.getenv("CMD_URL", "pi/browser/command/url")
STATE_URL = os.getenv("STATE_URL", "pi/browser/current_url")
CMD_REFRESH = os.getenv("CMD_REFRESH", "pi/browser/command/refresh")
CMD_RESTART = os.getenv("CMD_RESTART", "pi/system/command/restart")
CMD_BRIGHTNESS = os.getenv("CMD_BRIGHTNESS", "pi/brightness/command")
STATE_BRIGHTNESS = os.getenv("STATE_BRIGHTNESS", "pi/brightness/state")

DEFAULT_URL = os.getenv("DEFAULT_URL", "http://ukeplan.local:5000")



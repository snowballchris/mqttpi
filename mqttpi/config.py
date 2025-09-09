import os
from typing import Any, Dict

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # Will raise at runtime if config file is required


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _find_config_file() -> str:
    candidate = os.getenv("MQTTPI_CONFIG_FILE")
    if candidate and os.path.isfile(candidate):
        return candidate
    etc_path = "/etc/mqttpi/config.yaml"
    if os.path.isfile(etc_path):
        return etc_path
    local_path = os.path.join(_project_root(), "config.yaml")
    if os.path.isfile(local_path):
        return local_path
    return ""


def _load_yaml_config() -> Dict[str, Any]:
    path = _find_config_file()
    if not path:
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML is required but not installed. Install pyyaml or remove the config file.")
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


_CONFIG = _load_yaml_config()


# MQTT broker configuration (env vars override config file, which overrides defaults)
_mqtt = _CONFIG.get("mqtt", {}) if isinstance(_CONFIG.get("mqtt", {}), dict) else {}

MQTT_BROKER = os.getenv("MQTT_BROKER", _mqtt.get("broker", "homeassistant.local"))
MQTT_PORT = int(os.getenv("MQTT_PORT", str(_mqtt.get("port", 1883))))
MQTT_USER = os.getenv("MQTT_USER", _mqtt.get("username", "mqtt-user"))
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", _mqtt.get("password", "mqtt-password"))

# MQTT topics for commands and state
CMD_DISPLAY = os.getenv("CMD_DISPLAY", "pi/display/command")
STATE_DISPLAY = os.getenv("STATE_DISPLAY", "pi/display/state")
CMD_URL = os.getenv("CMD_URL", "pi/browser/command/url")
STATE_URL = os.getenv("STATE_URL", "pi/browser/current_url")
CMD_REFRESH = os.getenv("CMD_REFRESH", "pi/browser/command/refresh")
CMD_RESTART = os.getenv("CMD_RESTART", "pi/system/command/restart")
CMD_BRIGHTNESS = os.getenv("CMD_BRIGHTNESS", "pi/brightness/command")
STATE_BRIGHTNESS = os.getenv("STATE_BRIGHTNESS", "pi/brightness/state")

_app = _CONFIG.get("app", {}) if isinstance(_CONFIG.get("app", {}), dict) else {}
DEFAULT_URL = os.getenv("DEFAULT_URL", _app.get("default_url", "http://ukeplan.local:5000"))



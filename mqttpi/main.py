import json
import logging
import os
import platform
import shutil
import signal
import subprocess
import threading
import time
import sys
from typing import Optional

import paho.mqtt.client as mqtt

from . import config


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger("mqttpi")


 


# Globals
client: mqtt.Client
chromium_process: Optional[subprocess.Popen] = None
current_url: str = config.DEFAULT_URL
current_brightness: float = 0.5


def _set_display_env() -> None:
    os.environ["DISPLAY"] = ":0"


def get_display_state() -> str:
    """Query the current display state using xset (Linux only)."""
    try:
        _set_display_env()
        output = subprocess.check_output("xset -q", shell=True).decode("utf-8")
        return "OFF" if "Monitor is Off" in output else "ON"
    except Exception as e:
        logger.warning("Error in get_display_state: %s", e)
        return "unknown"


def get_memory_usage_percent() -> Optional[float]:
    """Calculate memory usage percentage (Linux: /proc/meminfo, otherwise None)."""
    try:
        meminfo = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split()
                key = parts[0].rstrip(":")
                meminfo[key] = int(parts[1])
        if "MemAvailable" in meminfo:
            used = meminfo["MemTotal"] - meminfo["MemAvailable"]
        else:
            used = meminfo["MemTotal"] - meminfo["MemFree"]
        return (used / meminfo["MemTotal"]) * 100
    except Exception as e:
        logger.warning("Error in get_memory_usage_percent: %s", e)
        return None


def monitor_display_state() -> None:
    """Continuously monitor the display state and publish immediately when it changes."""
    last_state = get_display_state()
    client.publish(config.STATE_DISPLAY, last_state)
    while True:
        current_state = get_display_state()
        if current_state != last_state:
            client.publish(config.STATE_DISPLAY, current_state)
            logger.info("Display state changed: %s", current_state)
            last_state = current_state
        time.sleep(5)


def publish_discovery() -> None:
    discovery_prefix = "homeassistant"
    device_info = {
        "identifiers": ["pi_ukeplan"],
        "name": "Raspberry Pi Ukeplan",
        "model": "Raspberry Pi 3b+",
        "manufacturer": "Raspberry Pi Foundation",
    }

    # Sensors
    payload = {
        "name": "Pi Disk Total",
        "state_topic": "pi/stats/disk_total",
        "unit_of_measurement": "GB",
        "icon": "mdi:harddisk",
        "unique_id": "pi_disk_total",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/sensor/pi_disk_total/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Pi Disk Free",
        "state_topic": "pi/stats/disk_free_gb",
        "unit_of_measurement": "GB",
        "icon": "mdi:harddisk",
        "unique_id": "pi_disk_free_gb",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/sensor/pi_disk_free_gb/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Pi Disk Free %",
        "state_topic": "pi/stats/disk_free_pct",
        "unit_of_measurement": "%",
        "icon": "mdi:harddisk",
        "unique_id": "pi_disk_free_pct",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/sensor/pi_disk_free_pct/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Pi CPU Load",
        "state_topic": "pi/stats/cpu_load",
        "unit_of_measurement": "%",
        "icon": "mdi:chip",
        "unique_id": "pi_cpu_load",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/sensor/pi_cpu_load/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Pi CPU Temperature",
        "state_topic": "pi/stats/cpu_temp",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "unique_id": "pi_cpu_temp",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/sensor/pi_cpu_temp/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Pi WiFi IP",
        "state_topic": "pi/stats/ip_address",
        "icon": "mdi:wifi",
        "unique_id": "pi_wifi_ip",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/sensor/pi_wifi_ip/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Pi Memory Usage",
        "state_topic": "pi/stats/memory_usage",
        "unit_of_measurement": "%",
        "icon": "mdi:memory",
        "unique_id": "pi_memory_usage",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/sensor/pi_memory_usage/config", json.dumps(payload), retain=True)

    # Controls
    payload = {
        "name": "Chromium URL",
        "command_topic": config.CMD_URL,
        "state_topic": config.STATE_URL,
        "unique_id": "pi_chromium_url",
        "device": device_info,
        "max": 255,
        "mode": "text",
    }
    client.publish(f"{discovery_prefix}/text/pi_chromium_url/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Default URL",
        "command_topic": config.CMD_URL,
        "payload_press": config.DEFAULT_URL,
        "unique_id": "pi_default_url",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/button/pi_default_url/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Pi Display Power",
        "command_topic": config.CMD_DISPLAY,
        "state_topic": config.STATE_DISPLAY,
        "payload_on": "ON",
        "payload_off": "OFF",
        "unique_id": "pi_display_power",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/switch/pi_display_power/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Refresh Website",
        "command_topic": config.CMD_REFRESH,
        "payload_press": "REFRESH",
        "unique_id": "pi_refresh_website",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/button/pi_refresh_website/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Restart Raspberry Pi",
        "command_topic": config.CMD_RESTART,
        "payload_press": "RESTART",
        "unique_id": "pi_restart",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/button/pi_restart/config", json.dumps(payload), retain=True)

    payload = {
        "name": "Pi Screen Brightness",
        "command_topic": config.CMD_BRIGHTNESS,
        "state_topic": config.STATE_BRIGHTNESS,
        "min": 0,
        "max": 1,
        "step": 0.01,
        "unique_id": "pi_screen_brightness",
        "device": device_info,
    }
    client.publish(f"{discovery_prefix}/number/pi_screen_brightness/config", json.dumps(payload), retain=True)


def on_connect(mqtt_client: mqtt.Client, _userdata, _flags, rc):
    logger.info("MQTT connected with code %s", rc)
    mqtt_client.subscribe(
        [
            (config.CMD_DISPLAY, 0),
            (config.CMD_URL, 0),
            (config.CMD_REFRESH, 0),
            (config.CMD_RESTART, 0),
            (config.CMD_BRIGHTNESS, 0),
        ]
    )
    publish_discovery()


def on_message(_client: mqtt.Client, _userdata, msg):
    global current_brightness
    topic = msg.topic
    payload = msg.payload.decode("utf-8").strip()
    if topic == config.CMD_DISPLAY:
        _set_display_env()
        if payload == "OFF":
            subprocess.call("xset dpms force off", shell=True)
            client.publish(config.STATE_DISPLAY, "OFF")
            logger.info("Screen OFF command executed")
        elif payload == "ON":
            subprocess.call("xset dpms force on", shell=True)
            client.publish(config.STATE_DISPLAY, "ON")
            logger.info("Screen ON command executed")
    elif topic == config.CMD_URL:
        logger.info("Loading new URL: %s", payload)
        launch_chromium(payload)
    elif topic == config.CMD_REFRESH:
        logger.info("Refreshing website")
        refresh_chromium()
    elif topic == config.CMD_RESTART:
        logger.info("Restarting Raspberry Pi")
        restart_pi()
    elif topic == config.CMD_BRIGHTNESS:
        try:
            brightness_val = float(payload)
            brightness_val = max(0, min(1, brightness_val))
            _set_display_env()
            subprocess.call(f"xrandr --output HDMI-1 --brightness {brightness_val}", shell=True)
            current_brightness = brightness_val
            client.publish(config.STATE_BRIGHTNESS, f"{brightness_val:.2f}")
            logger.info("Brightness set to %s", brightness_val)
        except Exception as e:
            logger.warning("Error setting brightness: %s", e)


def launch_chromium(url: str) -> None:
    global chromium_process, current_url
    if chromium_process:
        try:
            chromium_process.send_signal(signal.SIGTERM)
            chromium_process.wait(timeout=5)
        except Exception:
            subprocess.call("pkill -f chromium-browser", shell=True)
    chromium_process = subprocess.Popen([
        "chromium-browser",
        "--noerrdialogs",
        "--disable-infobars",
        "--kiosk",
        url,
    ])
    current_url = url
    client.publish(config.STATE_URL, current_url)


def refresh_chromium() -> None:
    try:
        window_id = (
            subprocess.check_output(
                "xdotool search --onlyvisible --class chromium-browser", shell=True
            )
            .decode()
            .split()[0]
        )
        subprocess.call(f"xdotool windowactivate {window_id} key ctrl+F5", shell=True)
        logger.info("Sent Ctrl+F5 to Chromium for cache bypass refresh")
    except Exception as e:
        logger.warning("Error during refresh: %s", e)


def restart_pi() -> None:
    logger.info("Restarting Raspberry Pi...")
    subprocess.call("sudo reboot", shell=True)


def _get_ip_address() -> str:
    try:
        ip_output = subprocess.check_output(
            "ip -4 addr show wlan0 | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){3}'",
            shell=True,
        )
        return ip_output.decode().strip()
    except subprocess.CalledProcessError:
        try:
            return subprocess.check_output("hostname -I", shell=True).decode().split()[0]
        except Exception:
            return "unknown"


def publish_system_stats() -> None:
    total, used, free = shutil.disk_usage("/")
    total_gb = total / (1024 ** 3)
    free_gb = free / (1024 ** 3)
    free_pct = (free / total) * 100
    load1 = os.getloadavg()[0]
    num_cores = os.cpu_count() or 1
    load_percent = (load1 / num_cores) * 100
    temp_c = 0.0
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp_c = int(f.read().strip()) / 1000.0
    except FileNotFoundError:
        pass
    ip_addr = _get_ip_address()

    mem_usage = get_memory_usage_percent() or 0

    client.publish("pi/stats/disk_total", f"{total_gb:.1f}")
    client.publish("pi/stats/disk_free_gb", f"{free_gb:.1f}")
    client.publish("pi/stats/disk_free_pct", f"{free_pct:.0f}")
    client.publish("pi/stats/cpu_load", f"{load_percent:.2f}")
    client.publish("pi/stats/cpu_temp", f"{temp_c:.1f}")
    client.publish("pi/stats/ip_address", ip_addr)
    client.publish("pi/stats/memory_usage", f"{mem_usage:.2f}")
    client.publish(config.STATE_URL, current_url)
    client.publish(config.STATE_BRIGHTNESS, f"{current_brightness:.2f}")
    logger.info("Published system stats via MQTT")


def run() -> None:
    if platform.system() != "Linux":
        logger.error("This application only runs on Linux.")
        sys.exit(1)
    global client
    client = mqtt.Client()
    client.username_pw_set(config.MQTT_USER, config.MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    client.loop_start()

    display_monitor_thread = threading.Thread(target=monitor_display_state, daemon=True)
    display_monitor_thread.start()

    launch_chromium(config.DEFAULT_URL)

    try:
        while True:
            publish_system_stats()
            time.sleep(120)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    run()



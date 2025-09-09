MQTT Pi Controller (Linux only)

This app connects to an MQTT broker and exposes topics to control a Raspberry Pi's display and Chromium kiosk. It also publishes system stats and Home Assistant discovery entities. The application only runs on Linux (intended for Raspberry Pi OS/Debian).

1) Configure (optional) via environment variables:

- MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
- DEFAULT_URL

2) Run (Linux only):

```bash
chmod +x ./bin/mqttpi
./bin/mqttpi
```

Note: The application exits on non-Linux systems.

Run as a service (Linux)

- Linux systemd: copy `services/mqttpi.service` to `/etc/systemd/system/`, adjust paths, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mqttpi.service
```

Topics

- Control: `pi/display/command`, `pi/browser/command/url`, `pi/browser/command/refresh`, `pi/system/command/restart`, `pi/brightness/command`
- State: `pi/display/state`, `pi/browser/current_url`, `pi/brightness/state`
- Stats: `pi/stats/*`



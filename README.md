MQTT Pi Controller

This app connects to an MQTT broker and exposes topics to control a Raspberry Pi's display and Chromium kiosk. It also publishes system stats and Home Assistant discovery entities.

Quick start (macOS/Linux):

1) Configure (optional) via environment variables:

- MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
- DEFAULT_URL

2) Run:

```bash
chmod +x ./bin/mqttpi
./bin/mqttpi
```

On macOS, display control and Chromium actions are no-ops; MQTT and stats still run. On Raspberry Pi (Linux), full functionality is enabled.

Run as a service

- macOS launchd: copy `services/mqttpi.plist` to `~/Library/LaunchAgents/`, adjust paths, then:

```bash
launchctl load -w ~/Library/LaunchAgents/mqttpi.plist
```

- Linux systemd: copy `services/mqttpi.service` to `/etc/systemd/system/`, adjust paths, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mqttpi.service
```

Topics

- Control: `pi/display/command`, `pi/browser/command/url`, `pi/browser/command/refresh`, `pi/system/command/restart`, `pi/brightness/command`
- State: `pi/display/state`, `pi/browser/current_url`, `pi/brightness/state`
- Stats: `pi/stats/*`



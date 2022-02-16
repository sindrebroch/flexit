# Flexit for HomeAssistant

![GitHub release (latest by date)](https://img.shields.io/github/v/release/sindrebroch/ha-flexit?style=flat-square)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/sindrebroch)

This integration uses an undocumented API, use at your own risk. This integration uses the same domain name as the official Flexit-integration, so in its current state you can't use both at the same time.

Tested with:

- Nordic S2
- Nordic S3
- Nordic S4
- Nordic CL4

## Features

### Climate-entity

- Preset modes:
  - Home
  - Away
  - Boost
- Operation modes:
  - Fan only
  - Heat
- Viewable modes:
  - Null
  - Off
  - Away
  - Home
  - High
  - Cooker hood
  - Fireplace
  - Forced ventilation

### Sensor-entities

- Extract temperature
- Exhaust temperature
- Outside temperature
- Supply temperature
- Room temperature

- Extract Fan Control Signal
- Extract Fan Speed
- Heat Exchanger Speed
- Supply Fan Control Signal
- Supply Fan Speed
- Additional Heater

### Binary sensor-entity

- Dirty filter
  - Hours since change
  - Hours until dirty
  - Filter change interval hours
- Alarm
  - Alarm Code A
  - Alarm Code B

## Requirements

- Your Flexit-unit needs to be connected to the Internet
- Unit needs to be registered in the Flexit Go-app

## Roadmap

- [ ] Fix binary_sensors not updating
- [ ] Be able to set all modes (Fireplace, Calendar missing)
- [ ] Service to set modes with modifications (delay, duration, override etc)

## Installation

<details>
  <summary>HACS (Recommanded)</summary>

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. Add this repository as a custom repository
3. Search for and install the "Flexit" integration.
4. Restart Home Assistant.
5. Add the `Flexit` integration to HA from the integration-page
6. Username and password is the same as in Flexit Go
</details>

<details>
  <summary>Manual installation</summary>

1. Download the `Source code (zip)` file from the
   [latest release](https://github.com/sindrebroch/ha-flexit/releases/latest).
2. Unpack the release and copy the `custom_components/flexit` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Restart Home Assistant.
4. Add the `Flexit` integration to HA from the integration-page
5. Username and password is the same as in Flexit Go
</details>

## Service information

### Service status

Service status can be found [here](https://status.climatixic.com/)

### API limitation

API is restricted to 50 calls/min or 500 calls/week. Defaults to polling every 30 minutes, this can be configured but be aware of API restrictions.

## Debugging

If something is not working properly, logs might help with debugging. To turn on debug-logging add this to your `configuration.yaml`

```
logger:
  default: info
  logs:
    custom_components.flexit: debug
```

PS: This will log various details, including all HTTP-requests for the Flexit-integration to your home-assistant.log. This includes your username and password in cleartext in your Token-requests.

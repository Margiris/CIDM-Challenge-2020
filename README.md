# CIDM-Challenge-2020 - Distance pinger

Program that writes distance values from ultrasonic sensor together with GPS coordinates and measurement time to specified file in CSV format.

All needed files are prepared in the `pi/` folder. If you don't intend to modify it, then clone this repository and [install](#installing).

## Downloading

Run `download.sh` only on device that you intend to use this for, then transfer `debs` and`pip` folders to `distance_pinger/` folder on your device.

> If you're not adding dependencies, you don't have to download anything. All currently needed files are already in the `distance_pinger/` folder.

## Packing

`pack_setup.sh` script adds everything the `distance_pinger` program needs (installer script, dependencies, python scripts) to one installer executable in `pi/payload/home/pi/`.

## Installing

Put everything from `/pi/` folder on the `boot` partition of a fresh _Raspberry Pi OS_ install.
It will self-install on the next boot.

> Non-fresh install might still work, but remember that the install script disables quite a few things, e.g. audio, 3D video driver, status LED, etc.

After installation the device will automatically connect to a wireless network that is defined in `pi/wpa_supplicant.conf`. Edit the file according to your network, or create a wireless network based on current configuration file.

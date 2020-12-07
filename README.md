# CIDM-Challenge-2020

## Downloading

Run `download.sh` only on device that you intend to use this for, then transfer `debs` and`pip` folders to `./distance_pinger` folder on your device.

## Packing

`pack_setup.sh` script adds everything the `distance_pinger` program needs to one installer executable in `pi/payload/home/pi/`.

## Installing

Put everything from `/pi/` folder on the `boot` partition of a fresh _Raspberry Pi OS_ install.
It will self-install on the next boot.

Non-fresh install might still work, but remember that the install script disables quite a few things, e.g. audio, 3D video driver, status LED, etc.

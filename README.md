# Falconia Beacon

Falconia Beacon is an ATTINY816-based, CR2032-powered LED beacon board used to make the Falconia rover visible to the SMCS Pi-in-the-sky satellite.

## What It Does

- Blinks onboard LEDs so the satellite can detect the rover location.
- Uses a potentiometer to enable or disable the blinking program.
- Supports I2C control at address `0x42`.

## Project Layout

- `PCB/`  
  Hardware design and manufacturing assets:
  - KiCad schematic and PCB files
  - 3D models and custom footprints/symbol libraries
  - Panelization and production outputs

- `src/`  
  Firmware source flashed to the board by default:
  - Main beacon firmware and related examples
  - Build files (Makefile)

## Hardware Summary

- MCU: Microchip ATTINY816
- Power: CR2032 coin cell
- Interface: I2C (address `0x42`)
- User control: Potentiometer (blink program on/off)

## Firmware

The default board firmware lives in `src/` and is intended to be the code programmed onto production boards unless otherwise noted.

Typical workflow:

1. Build firmware from the `src/` directory.
2. Flash using your ATTINY816 programming setup.
3. Validate LED blink behavior and I2C response at address `0x42`.

## Notes

- Hardware and firmware are versioned together in this repository.
- For board-level updates, start in `PCB/`.
- For behavior/protocol updates, start in `src/`.

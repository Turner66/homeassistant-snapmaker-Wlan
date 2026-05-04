# homeassistant-snapmaker-wlan

Home Assistant custom integration for the **Snapmaker J1**  
(WiFi-based control inspired by the official Snapmaker Luban software)

---

## Overview

This project aims to build a **native Home Assistant integration** for the
Snapmaker J1 3D printer.

Key points:
- Snapmaker J1 is **WiFi-only**
- Communication is done via local network APIs
- Behavior should match Snapmaker Luban where possible

---

## Technical Background

Reference software:
- Snapmaker **Luban** (official desktop software)

Relevant characteristics:
- UDP discovery on port **20054**
- HTTP API on port **8080**
- JSON-based communication

Luban can:
- Read printer state
- Read nozzle and bed temperatures
- Read print progress
- Start, pause, and stop print jobs

This integration reimplements these capabilities in a simplified,
Home-Assistant-native way.

---

## Goal

- Status sensors (idle / printing / paused)
- Temperature sensors (bed / extruders)
- Print progress sensor
- Control buttons (pause / resume / stop)

Minimal, stable, and readable implementation.

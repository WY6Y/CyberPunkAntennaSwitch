# WY6YPi Antenna Switch
# Copyright (c) 2025 Stephen Houser
# Licensed under CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)
#!/usr/bin/env python3
import sys
import RPi.GPIO as GPIO
import time

# GPIO pin mappings
RELAY_PINS = {'0': None, '1': 23, '2': 27, '3': 18}  # Relays 1-3 for antennas (Doublet, Emcomm III-B, Aux)
SHACK_RELAY_PIN = 17  # Relay 4 for Shack (main coax)
GROUND_PIN = 22  # Ground pin (not wired yet)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initialize relay pins (high-level triggering: LOW = off, HIGH = on)
for pin in RELAY_PINS.values():
    if pin:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Start with all relays off
GPIO.setup(SHACK_RELAY_PIN, GPIO.OUT)
GPIO.output(SHACK_RELAY_PIN, GPIO.LOW)  # Start with Shack relay off
GPIO.setup(GROUND_PIN, GPIO.OUT)
GPIO.output(GROUND_PIN, GPIO.LOW)  # Ground off initially

def cleanup():
    for pin in RELAY_PINS.values():
        if pin:
            GPIO.output(pin, GPIO.LOW)
    GPIO.output(SHACK_RELAY_PIN, GPIO.LOW)
    GPIO.output(GROUND_PIN, GPIO.LOW)
    GPIO.cleanup()

try:
    state = sys.argv[1]
    if state not in RELAY_PINS:
        raise ValueError("Invalid state")

    # First, turn off all relays and activate ground (failsafe)
    for pin in RELAY_PINS.values():
        if pin:
            GPIO.output(pin, GPIO.LOW)  # Deactivate all antenna relays
    GPIO.output(SHACK_RELAY_PIN, GPIO.LOW)  # Deactivate Shack relay
    GPIO.output(GROUND_PIN, GPIO.HIGH)  # Ground all antennas

    # If not STORM MODE, activate the selected relay and Shack relay
    if state != '0':
        GPIO.output(RELAY_PINS[state], GPIO.HIGH)  # Activate selected antenna relay
        GPIO.output(SHACK_RELAY_PIN, GPIO.HIGH)  # Activate Shack relay to connect main coax
        GPIO.output(GROUND_PIN, GPIO.LOW)  # Release ground

    # Update state file
    with open('/home/user/antenna_switch/state.txt', 'w') as f:
        f.write(state)
    print(f"Switched to state {state}")

    time.sleep(0.1)

except Exception as e:
    print(f"Error: {e}")
    cleanup()
    sys.exit(1)

# Do not cleanup immediately to hold the GPIO state
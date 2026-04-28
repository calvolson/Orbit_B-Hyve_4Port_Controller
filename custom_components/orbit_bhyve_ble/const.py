"""Constants for the Orbit B-Hyve BLE integration."""

DOMAIN = "orbit_bhyve_ble"

# GATT characteristic UUIDs
AES_CHAR = "00006c71-fe32-4f58-8b78-98e42b2c047f"
WRITE_CHAR = "00006c72-fe32-4f58-8b78-98e42b2c047f"
READ_CHAR = "00006c73-fe32-4f58-8b78-98e42b2c047f"

# BLE service UUID (used for auto-discovery)
SERVICE_UUID = "0000fe32-0000-1000-8000-00805f9b34fb"

# Inner message header
MSG_HEADER = bytes([0xAA, 0x77, 0x5A, 0x0F])

# Config keys
CONF_NETWORK_KEY = "network_key"
CONF_NUM_ZONES = "num_zones"

# Defaults
DEFAULT_NUM_ZONES = 4
DEFAULT_DURATION = 600  # 10 minutes

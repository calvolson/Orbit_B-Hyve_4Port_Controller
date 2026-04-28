"""Orbit B-Hyve BLE Sprinkler Controller for Home Assistant.

Direct Bluetooth control of Orbit B-Hyve XD hose timers using HA's
built-in Bluetooth manager. No cloud, no Wi-Fi hub, no separate bridge.

WARNING: Do NOT update your B-Hyve device firmware. The protocol used
by this integration was reverse-engineered against firmware 0107. A
firmware update could change the encryption protocol and break
compatibility. If the B-Hyve app prompts you to update, decline it.
"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .bhyve_device import BHyveDevice
from .const import DOMAIN, CONF_NETWORK_KEY, CONF_NUM_ZONES, DEFAULT_NUM_ZONES

PLATFORMS = [Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Orbit B-Hyve BLE from a config entry."""
    address = entry.data[CONF_ADDRESS]
    network_key = entry.data[CONF_NETWORK_KEY]
    num_zones = entry.data.get(CONF_NUM_ZONES, DEFAULT_NUM_ZONES)

    device = BHyveDevice(hass, address, network_key, num_zones)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

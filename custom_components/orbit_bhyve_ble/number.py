"""Number platform for B-Hyve BLE run-time controls.

These entities are created automatically when the integration is set up, so
users get per-zone run-time controls (and a global run-time ceiling) without
hand-editing configuration.yaml. They replace the optional input_number
helpers documented in blueprints/.../example_helpers.yaml.

- number.bhyve_zone_N_runtime  — read by the "Per-Valve Run Time" blueprint.
- number.bhyve_duration        — the device-side ceiling; pushed onto the
                                 BHyveDevice so the switch tells the hardware
                                 how long to run.
"""

import logging

from homeassistant.components.number import (
    NumberMode,
    RestoreNumber,
    ENTITY_ID_FORMAT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEFAULT_DURATION

_LOGGER = logging.getLogger(__name__)

# Per-valve run time slider bounds (minutes).
RUNTIME_MIN = 0
RUNTIME_MAX = 60
RUNTIME_STEP = 1

# Run-time ceiling bounds (minutes).
DURATION_MIN = 1
DURATION_MAX = 120
DURATION_STEP = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up B-Hyve run-time number entities from a config entry."""
    device = hass.data[DOMAIN][entry.entry_id]

    entities: list = [
        BHyveRuntimeNumber(hass, device, zone)
        for zone in range(1, device.num_zones + 1)
    ]
    entities.append(BHyveDurationNumber(hass, device))
    async_add_entities(entities)


class _BHyveNumberBase(RestoreNumber):
    """Shared device wiring and value restore for B-Hyve number entities."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(self, device):
        self._device = device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.address)},
            "name": f"B-Hyve {device.address[-5:]}",
            "manufacturer": "Orbit Irrigation",
            "model": "B-Hyve XD (HT-34)",
            "sw_version": "0107",
        }

    async def async_added_to_hass(self) -> None:
        """Restore the last value the user set (numbers have no device state)."""
        await super().async_added_to_hass()
        last = await self.async_get_last_number_data()
        if last is not None and last.native_value is not None:
            self._attr_native_value = last.native_value
        self._apply_value()

    def _apply_value(self) -> None:
        """Hook for subclasses to propagate the restored value."""

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self._apply_value()
        self.async_write_ha_state()


class BHyveRuntimeNumber(_BHyveNumberBase):
    """Per-valve run time (minutes) read by the per-valve blueprint.

    Defaults to 0, which the blueprint treats as "no run time set" and refuses
    to run — a deliberate safety default matching the helper-based design.
    """

    _attr_native_min_value = RUNTIME_MIN
    _attr_native_max_value = RUNTIME_MAX
    _attr_native_step = RUNTIME_STEP
    _attr_native_unit_of_measurement = "min"
    _attr_icon = "mdi:timer-outline"

    def __init__(self, hass: HomeAssistant, device, zone: int):
        super().__init__(device)
        self._zone = zone
        self._attr_native_value = 0
        mac_clean = device.address.replace(":", "").lower()
        self._attr_unique_id = f"bhyve_{mac_clean}_zone_{zone}_runtime"
        self._attr_name = f"Zone {zone} run time"
        # Force a predictable object id so the blueprint's default helper
        # prefix (number.bhyve_zone_) resolves. HA appends _2, _3, … if a
        # second device would otherwise collide.
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, f"bhyve_zone_{zone}_runtime", hass=hass
        )

    def _apply_value(self) -> None:
        # Switch reads device.zone_runtimes[zone] (seconds) when this zone
        # turns on, falling back to the global ceiling when it is 0.
        self._device.zone_runtimes[self._zone] = int(self._attr_native_value) * 60


class BHyveDurationNumber(_BHyveNumberBase):
    """Device-side run-time ceiling (minutes).

    The integration tells the device to run for this long when a zone turns
    on; the device stops itself when it elapses. Pushed onto the BHyveDevice
    so the switch uses the right per-device value.
    """

    _attr_native_min_value = DURATION_MIN
    _attr_native_max_value = DURATION_MAX
    _attr_native_step = DURATION_STEP
    _attr_native_unit_of_measurement = "min"
    _attr_icon = "mdi:timer-lock-outline"

    def __init__(self, hass: HomeAssistant, device):
        super().__init__(device)
        self._attr_native_value = DEFAULT_DURATION // 60
        mac_clean = device.address.replace(":", "").lower()
        self._attr_unique_id = f"bhyve_{mac_clean}_duration"
        self._attr_name = "Max run time"
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, "bhyve_duration", hass=hass
        )

    def _apply_value(self) -> None:
        # Switch reads device.duration_ceiling (seconds) when a zone turns on.
        self._device.duration_ceiling = int(self._attr_native_value) * 60

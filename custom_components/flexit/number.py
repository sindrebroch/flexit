"""Number platform for Flexit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple, Literal

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.components.number.const import (
    DEFAULT_MAX_VALUE,
    DEFAULT_MIN_VALUE,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN as FLEXIT_DOMAIN
from .coordinator import FlexitDataUpdateCoordinator
from .models import Entity


@dataclass
class FlexitNumberEntityDescription(NumberEntityDescription):
    """A class that describes number entities."""

    native_min_value: float | None = None
    native_max_value: float | None = None
    entity: str | None = None


NUMBERS: Tuple[FlexitNumberEntityDescription, ...] = (
    FlexitNumberEntityDescription(
        key=Entity.AWAY_DELAY.value,
        name="Delay Away Mode",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.CONFIG,
        native_min_value=0.0,
        native_max_value=300.0,
        icon="mdi:timer",
    ),
    FlexitNumberEntityDescription(
        key=Entity.BOOST_DURATION.value,
        name="Duration Boost Temporary",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.CONFIG,
        native_min_value=1.0,
        native_max_value=360.0,
        icon="mdi:timer",
    ),
    FlexitNumberEntityDescription(
        key=Entity.FIREPLACE_DURATION.value,
        name="Duration Fireplace",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.CONFIG,
        native_min_value=0.0,
        native_max_value=360.0,
        icon="mdi:timer",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Flexit number."""

    coordinator: FlexitDataUpdateCoordinator = hass.data[FLEXIT_DOMAIN][entry.entry_id]

    for description in NUMBERS:
        if description.key == Entity.AWAY_DELAY.value:
            async_add_entities([FlexitAwayDelayNumber(coordinator, description)])
        if description.key == Entity.BOOST_DURATION.value:
            async_add_entities([FlexitBoostDurationNumber(coordinator, description)])
        if description.key == Entity.FIREPLACE_DURATION.value:
            async_add_entities(
                [FlexitFireplaceDurationNumber(coordinator, description)]
            )


class FlexitNumber(CoordinatorEntity, NumberEntity):
    """Define a Flexit entity."""

    sensor_data: Any
    coordinator: FlexitDataUpdateCoordinator
    entity_description: FlexitNumberEntityDescription

    def __init__(
        self,
        coordinator: FlexitDataUpdateCoordinator,
        description: FlexitNumberEntityDescription,
    ) -> None:
        """Initialize."""

        super().__init__(coordinator)
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{description.key}"
        self._attr_device_info = coordinator._attr_device_info

        self._attr_native_step = 1
        self._attr_mode: Literal["auto", "slider", "box"] = NumberMode.AUTO
        self._attr_native_min_value = description.native_min_value or DEFAULT_MIN_VALUE
        self._attr_native_max_value = description.native_max_value or DEFAULT_MAX_VALUE

        self.update_from_data()

    def update_from_data(self) -> None:
        """Update attributes based on new data."""
        self.sensor_data = self.coordinator.data.__getattribute__(
            self.entity_description.key
        )

    @property
    def native_value(self) -> float:
        return self.sensor_data

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""

        self.update_from_data()
        super()._handle_coordinator_update()


class FlexitFireplaceDurationNumber(FlexitNumber):
    """Define a Flexit entity."""

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if await self.coordinator.api.set_fireplace_duration(int(value)):
            self.sensor_data = value
        await self.coordinator.async_request_refresh()


class FlexitBoostDurationNumber(FlexitNumber):
    """Define a Flexit entity."""

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if await self.coordinator.api.set_boost_duration(int(value)):
            self.sensor_data = value
        await self.coordinator.async_request_refresh()


class FlexitAwayDelayNumber(FlexitNumber):
    """Define a Flexit entity."""

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if await self.coordinator.api.set_away_delay(int(value)):
            self.sensor_data = value
        await self.coordinator.async_request_refresh()

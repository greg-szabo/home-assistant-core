"""Support for YouTube Sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ICON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import YouTubeDataUpdateCoordinator
from .const import (
    ATTR_LATEST_VIDEO,
    ATTR_SUBSCRIBER_COUNT,
    ATTR_THUMBNAIL,
    ATTR_TITLE,
    ATTR_VIDEO_ID,
    COORDINATOR,
    DOMAIN,
)
from .entity import YouTubeChannelEntity


@dataclass
class YouTubeMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], StateType]
    entity_picture_fn: Callable[[Any], str]
    attributes_fn: Callable[[Any], dict[str, Any]] | None


@dataclass
class YouTubeSensorEntityDescription(SensorEntityDescription, YouTubeMixin):
    """Describes YouTube sensor entity."""


SENSOR_TYPES = [
    YouTubeSensorEntityDescription(
        key="latest_upload",
        translation_key="latest_upload",
        icon="mdi:youtube",
        value_fn=lambda channel: channel[ATTR_LATEST_VIDEO][ATTR_TITLE],
        entity_picture_fn=lambda channel: channel[ATTR_LATEST_VIDEO][ATTR_THUMBNAIL],
        attributes_fn=lambda channel: {
            ATTR_VIDEO_ID: channel[ATTR_LATEST_VIDEO][ATTR_VIDEO_ID]
        },
    ),
    YouTubeSensorEntityDescription(
        key="subscribers",
        translation_key="subscribers",
        icon="mdi:youtube-subscription",
        native_unit_of_measurement="subscribers",
        value_fn=lambda channel: channel[ATTR_SUBSCRIBER_COUNT],
        entity_picture_fn=lambda channel: channel[ATTR_ICON],
        attributes_fn=None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the YouTube sensor."""
    coordinator: YouTubeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]
    async_add_entities(
        YouTubeSensor(coordinator, sensor_type, channel_id)
        for channel_id in coordinator.data
        for sensor_type in SENSOR_TYPES
    )


class YouTubeSensor(YouTubeChannelEntity, SensorEntity):
    """Representation of a YouTube sensor."""

    entity_description: YouTubeSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        return self.entity_description.value_fn(self.coordinator.data[self._channel_id])

    @property
    def entity_picture(self) -> str:
        """Return the value reported by the sensor."""
        return self.entity_description.entity_picture_fn(
            self.coordinator.data[self._channel_id]
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the extra state attributes."""
        if self.entity_description.attributes_fn:
            return self.entity_description.attributes_fn(
                self.coordinator.data[self._channel_id]
            )
        return None

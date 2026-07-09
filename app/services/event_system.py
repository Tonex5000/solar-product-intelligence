"""Event System for Solar Simulation Engine."""
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

from app.schemas.simulation import EventType, Severity, SimulationEvent


@dataclass
class Event:
    """Internal event representation."""
    day: int
    event_type: EventType
    severity: Severity
    message: str
    component: str
    details: dict = field(default_factory=dict)


class EventLogger:
    """Event logging system for simulation events."""

    def __init__(self):
        """Initialize the event logger."""
        self.events: list[Event] = []
        self._event_counts = {
            EventType.WARNING: 0,
            EventType.DAMAGE: 0,
            EventType.FAILURE: 0,
            EventType.INFO: 0,
            EventType.MILESTONE: 0,
        }

    def log(
        self,
        day: int,
        event_type: EventType,
        severity: Severity,
        message: str,
        component: str,
        details: Optional[dict] = None
    ) -> Event:
        """Log an event."""
        event = Event(
            day=day,
            event_type=event_type,
            severity=severity,
            message=message,
            component=component,
            details=details or {}
        )
        self.events.append(event)
        self._event_counts[event_type] = self._event_counts.get(event_type, 0) + 1
        return event

    def log_warning(
        self,
        day: int,
        message: str,
        component: str,
        severity: Severity = Severity.MEDIUM,
        details: Optional[dict] = None
    ) -> Event:
        """Log a warning event."""
        return self.log(day, EventType.WARNING, severity, message, component, details)

    def log_damage(
        self,
        day: int,
        message: str,
        component: str,
        severity: Severity = Severity.HIGH,
        details: Optional[dict] = None
    ) -> Event:
        """Log a damage event."""
        return self.log(day, EventType.DAMAGE, severity, message, component, details)

    def log_failure(
        self,
        day: int,
        message: str,
        component: str,
        details: Optional[dict] = None
    ) -> Event:
        """Log a failure event."""
        return self.log(day, EventType.FAILURE, Severity.CRITICAL, message, component, details)

    def log_info(
        self,
        day: int,
        message: str,
        component: str,
        details: Optional[dict] = None
    ) -> Event:
        """Log an info event."""
        return self.log(day, EventType.INFO, Severity.LOW, message, component, details)

    def log_milestone(
        self,
        day: int,
        message: str,
        component: str = "system",
        details: Optional[dict] = None
    ) -> Event:
        """Log a milestone event."""
        return self.log(day, EventType.MILESTONE, Severity.LOW, message, component, details)

    def get_events(self) -> list[Event]:
        """Get all logged events."""
        return self.events

    def get_events_by_type(self, event_type: EventType) -> list[Event]:
        """Get events filtered by type."""
        return [e for e in self.events if e.event_type == event_type]

    def get_events_by_day(self, day: int) -> list[Event]:
        """Get events for a specific day."""
        return [e for e in self.events if e.day == day]

    def get_event_counts(self) -> dict[EventType, int]:
        """Get count of events by type."""
        return self._event_counts.copy()

    def get_first_failure_day(self) -> Optional[int]:
        """Get the day of the first failure event."""
        failures = self.get_events_by_type(EventType.FAILURE)
        return failures[0].day if failures else None

    def clear(self) -> None:
        """Clear all events."""
        self.events = []
        self._event_counts = {
            EventType.WARNING: 0,
            EventType.DAMAGE: 0,
            EventType.FAILURE: 0,
            EventType.INFO: 0,
            EventType.MILESTONE: 0,
        }

    def to_simulation_events(self) -> list[SimulationEvent]:
        """Convert internal events to SimulationEvent schema."""
        return [
            SimulationEvent(
                day=e.day,
                type=e.event_type,
                severity=e.severity,
                message=e.message,
                component=e.component,
                details=e.details if e.details else None
            )
            for e in self.events
        ]

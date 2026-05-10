from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    rider = "rider"
    driver = "driver"


class RideStatus(str, Enum):
    requested = "requested"
    offered = "offered"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

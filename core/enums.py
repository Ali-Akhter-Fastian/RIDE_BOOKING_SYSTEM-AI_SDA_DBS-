from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    rider = "rider"
    driver = "driver"

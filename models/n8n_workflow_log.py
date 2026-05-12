from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class N8nWorkflowLog:
    id: UUID
    workflow_name: str
    status: str
    source: str
    related_entity_type: str | None
    related_entity_id: UUID | None
    request_payload: dict[str, Any] | None
    response_payload: dict[str, Any] | None
    error_message: str | None
    triggered_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, record: object) -> "N8nWorkflowLog":
        return cls(
            id=record["id"],
            workflow_name=record["workflow_name"],
            status=record["status"],
            source=record["source"],
            related_entity_type=record.get("related_entity_type"),
            related_entity_id=record.get("related_entity_id"),
            request_payload=record.get("request_payload"),
            response_payload=record.get("response_payload"),
            error_message=record.get("error_message"),
            triggered_at=record["triggered_at"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
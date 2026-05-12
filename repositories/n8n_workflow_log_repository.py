from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import asyncpg

from db.queries.n8n_workflow_log_queries import (
    INSERT_N8N_WORKFLOW_LOG,
    SELECT_N8N_WORKFLOW_LOG_BY_ID,
    SELECT_N8N_WORKFLOW_LOGS_BY_ENTITY,
    SELECT_N8N_WORKFLOW_LOGS_BY_WORKFLOW_NAME,
)
from models.n8n_workflow_log import N8nWorkflowLog


class N8nWorkflowLogRepository:
    def __init__(self, connection: asyncpg.Connection) -> None:
        self.connection = connection

    async def create_log(
        self,
        workflow_name: str,
        status: str,
        *,
        source: str = "app",
        related_entity_type: str | None = None,
        related_entity_id: UUID | None = None,
        request_payload: dict[str, Any] | None = None,
        response_payload: dict[str, Any] | None = None,
        error_message: str | None = None,
        triggered_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        log_id: UUID | None = None,
    ) -> N8nWorkflowLog:
        now = datetime.now(timezone.utc)
        triggered_at = triggered_at or now
        created_at = created_at or now
        updated_at = updated_at or now
        log_id = log_id or uuid4()

        record = await self.connection.fetchrow(
            INSERT_N8N_WORKFLOW_LOG,
            log_id,
            workflow_name,
            status,
            source,
            related_entity_type,
            related_entity_id,
            json.dumps(request_payload) if request_payload else None,
            json.dumps(response_payload) if response_payload else None,
            error_message,
            triggered_at,
            created_at,
            updated_at,
        )
        if record is None:
            raise RuntimeError("Failed to create n8n workflow log")
        return N8nWorkflowLog.from_record(record)

    async def get_log_by_id(self, log_id: UUID) -> N8nWorkflowLog | None:
        record = await self.connection.fetchrow(SELECT_N8N_WORKFLOW_LOG_BY_ID, log_id)
        if record is None:
            return None
        return N8nWorkflowLog.from_record(record)

    async def get_logs_by_workflow_name(self, workflow_name: str) -> list[N8nWorkflowLog]:
        records = await self.connection.fetch(
            SELECT_N8N_WORKFLOW_LOGS_BY_WORKFLOW_NAME,
            workflow_name,
        )
        return [N8nWorkflowLog.from_record(record) for record in records]

    async def get_logs_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
    ) -> list[N8nWorkflowLog]:
        records = await self.connection.fetch(
            SELECT_N8N_WORKFLOW_LOGS_BY_ENTITY,
            entity_type,
            entity_id,
        )
        return [N8nWorkflowLog.from_record(record) for record in records]
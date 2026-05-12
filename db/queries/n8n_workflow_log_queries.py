from __future__ import annotations

INSERT_N8N_WORKFLOW_LOG = """
    INSERT INTO n8n_workflow_log (
        id,
        workflow_name,
        status,
        source,
        related_entity_type,
        related_entity_id,
        request_payload,
        response_payload,
        error_message,
        triggered_at,
        created_at,
        updated_at
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb, $9, $10, $11, $12)
    RETURNING *;
"""

SELECT_N8N_WORKFLOW_LOG_BY_ID = """
    SELECT *
    FROM n8n_workflow_log
    WHERE id = $1;
"""

SELECT_N8N_WORKFLOW_LOGS_BY_WORKFLOW_NAME = """
    SELECT *
    FROM n8n_workflow_log
    WHERE workflow_name = $1
    ORDER BY triggered_at DESC;
"""

SELECT_N8N_WORKFLOW_LOGS_BY_ENTITY = """
    SELECT *
    FROM n8n_workflow_log
    WHERE related_entity_type = $1
      AND related_entity_id = $2
    ORDER BY triggered_at DESC;
"""
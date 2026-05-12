from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3f2a9b8d4e1"
down_revision: Union[str, tuple[str, str], None] = "007_merge_006_heads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS n8n_workflow_log (
            id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
            workflow_name       VARCHAR(100)  NOT NULL,
            status              VARCHAR(20)   NOT NULL CHECK (status IN ('triggered', 'success', 'failed', 'fallback')),
            source              VARCHAR(50)   NOT NULL DEFAULT 'app',
            related_entity_type VARCHAR(50),
            related_entity_id   UUID,
            request_payload     JSONB,
            response_payload    JSONB,
            error_message       TEXT,
            triggered_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW()
        );
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS idx_n8n_workflow_log_workflow_name ON n8n_workflow_log (workflow_name);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_n8n_workflow_log_status ON n8n_workflow_log (status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_n8n_workflow_log_triggered_at ON n8n_workflow_log (triggered_at DESC);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_n8n_workflow_log_entity ON n8n_workflow_log (related_entity_type, related_entity_id);")

    op.execute(
        """
        CREATE OR REPLACE FUNCTION log_n8n_workflow_from_rides()
        RETURNS TRIGGER AS $$
        DECLARE
            workflow_label VARCHAR(100);
        BEGIN
            workflow_label := CASE NEW.status
                WHEN 'offered' THEN 'driver_ranking'
                WHEN 'accepted' THEN 'ride_accepted'
                WHEN 'completed' THEN 'ride_completed'
                WHEN 'cancelled' THEN 'ride_cancelled'
                ELSE NULL
            END;

            IF workflow_label IS NOT NULL AND (
                TG_OP = 'INSERT' OR OLD.status IS DISTINCT FROM NEW.status
            ) THEN
                INSERT INTO n8n_workflow_log (
                    workflow_name,
                    status,
                    source,
                    related_entity_type,
                    related_entity_id,
                    request_payload,
                    triggered_at,
                    created_at,
                    updated_at
                ) VALUES (
                    workflow_label,
                    'triggered',
                    'db_trigger',
                    'ride',
                    NEW.id,
                    jsonb_build_object(
                        'ride_id', NEW.id,
                        'rider_id', NEW.rider_id,
                        'driver_id', NEW.driver_id,
                        'status', NEW.status,
                        'origin', NEW.origin,
                        'destination', NEW.destination,
                        'ride_type', NEW.ride_type
                    ),
                    NOW(),
                    NOW(),
                    NOW()
                );
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_log_n8n_workflow_from_rides
        AFTER INSERT OR UPDATE OF status ON rides
        FOR EACH ROW
        EXECUTE FUNCTION log_n8n_workflow_from_rides();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION log_n8n_workflow_from_payments()
        RETURNS TRIGGER AS $$
        DECLARE
            workflow_label VARCHAR(100);
        BEGIN
            workflow_label := CASE NEW.status
                WHEN 'failed' THEN 'payment_failed'
                WHEN 'completed' THEN 'payment_completed'
                WHEN 'processing' THEN 'payment_processing'
                ELSE NULL
            END;

            IF workflow_label IS NOT NULL AND (
                TG_OP = 'INSERT' OR OLD.status IS DISTINCT FROM NEW.status
            ) THEN
                INSERT INTO n8n_workflow_log (
                    workflow_name,
                    status,
                    source,
                    related_entity_type,
                    related_entity_id,
                    request_payload,
                    triggered_at,
                    created_at,
                    updated_at
                ) VALUES (
                    workflow_label,
                    'triggered',
                    'db_trigger',
                    'payment',
                    NEW.id,
                    jsonb_build_object(
                        'payment_id', NEW.id,
                        'ride_id', NEW.ride_id,
                        'user_id', NEW.user_id,
                        'amount', NEW.amount,
                        'status', NEW.status,
                        'payment_method', NEW.payment_method,
                        'transaction_id', NEW.transaction_id
                    ),
                    NOW(),
                    NOW(),
                    NOW()
                );
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_log_n8n_workflow_from_payments
        AFTER INSERT OR UPDATE OF status ON payments
        FOR EACH ROW
        EXECUTE FUNCTION log_n8n_workflow_from_payments();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_log_n8n_workflow_from_payments ON payments;")
    op.execute("DROP FUNCTION IF EXISTS log_n8n_workflow_from_payments();")
    op.execute("DROP TRIGGER IF EXISTS trg_log_n8n_workflow_from_rides ON rides;")
    op.execute("DROP FUNCTION IF EXISTS log_n8n_workflow_from_rides();")
    op.execute("DROP TABLE IF EXISTS n8n_workflow_log;")
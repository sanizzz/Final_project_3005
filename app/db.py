"""Database helpers used by the CLI."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from models import Base


# Direct connection using psycopg2 connect_args to avoid URL encoding issues
engine = create_engine(
    "postgresql+psycopg2://",
    connect_args={
        "host": "127.0.0.1",
        "port": 5432,
        "dbname": "Health and Fitness club",
        "user": "postgres",
        "password": "Saksan31!",
    },
    echo=False,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a managed SQLAlchemy session."""
    session: Session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create tables for all models."""
    Base.metadata.create_all(engine)
    _ensure_db_extras()


def _ensure_db_extras() -> None:
    """Create the required view, trigger, and indexes if they do not exist."""
    statements = [
        """
        CREATE OR REPLACE VIEW member_dashboard_view AS
        SELECT
            m.member_id,
            m.full_name,
            m.email,
            m.phone,
            goal.goal_type,
            goal.target_value,
            goal.target_date,
            metric.recorded_at AS latest_metric_at,
            metric.weight_kg,
            metric.heart_rate_bpm,
            metric.body_fat_percent
        FROM member m
        LEFT JOIN LATERAL (
            SELECT goal_type, target_value, target_date
            FROM fitnessgoal
            WHERE member_id = m.member_id AND is_active IS TRUE
            ORDER BY target_date DESC, goal_id DESC
            LIMIT 1
        ) AS goal ON TRUE
        LEFT JOIN LATERAL (
            SELECT recorded_at, weight_kg, heart_rate_bpm, body_fat_percent
            FROM healthmetric
            WHERE member_id = m.member_id
            ORDER BY recorded_at DESC, metric_id DESC
            LIMIT 1
        ) AS metric ON TRUE;
        """,
        """
        CREATE OR REPLACE FUNCTION check_class_capacity()
        RETURNS trigger AS $$
        DECLARE
            current_count integer;
            capacity integer;
        BEGIN
            SELECT COUNT(*) INTO current_count
            FROM classregistration
            WHERE class_id = NEW.class_id;

            SELECT max_capacity INTO capacity
            FROM fitnessclass
            WHERE class_id = NEW.class_id;

            IF capacity IS NULL THEN
                RAISE EXCEPTION 'Class % does not exist', NEW.class_id;
            END IF;

            IF current_count >= capacity THEN
                RAISE EXCEPTION 'Class % is full', NEW.class_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
        "DROP TRIGGER IF EXISTS trg_check_class_capacity ON classregistration;",
        """
        CREATE TRIGGER trg_check_class_capacity
        BEFORE INSERT ON classregistration
        FOR EACH ROW
        EXECUTE FUNCTION check_class_capacity();
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_classregistration_class_id
        ON classregistration (class_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_ptsession_trainer_start_time
        ON ptsession (trainer_id, start_time);
        """,
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))

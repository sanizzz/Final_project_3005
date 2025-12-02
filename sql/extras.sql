-- extras.sql
-- VIEW, TRIGGER FUNCTION, TRIGGER, and INDEX statements

-- =============================================================================
-- VIEW: Member Dashboard View
-- Shows each member with their active goal and latest health metric
-- =============================================================================
CREATE OR REPLACE VIEW MemberDashboardView AS
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
FROM Member m
LEFT JOIN LATERAL (
    SELECT goal_type, target_value, target_date
    FROM FitnessGoal
    WHERE member_id = m.member_id AND is_active IS TRUE
    ORDER BY target_date DESC, goal_id DESC
    LIMIT 1
) AS goal ON TRUE
LEFT JOIN LATERAL (
    SELECT recorded_at, weight_kg, heart_rate_bpm, body_fat_percent
    FROM HealthMetric
    WHERE member_id = m.member_id
    ORDER BY recorded_at DESC, metric_id DESC
    LIMIT 1
) AS metric ON TRUE;

-- =============================================================================
-- TRIGGER FUNCTION: Check Class Capacity
-- Prevents registration if class is already full
-- =============================================================================
CREATE OR REPLACE FUNCTION check_class_capacity()
RETURNS TRIGGER AS $$
DECLARE
    current_count INTEGER;
    capacity INTEGER;
BEGIN
    SELECT COUNT(*) INTO current_count
    FROM ClassRegistration
    WHERE class_id = NEW.class_id;

    SELECT max_capacity INTO capacity
    FROM FitnessClass
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

-- =============================================================================
-- TRIGGER: Apply capacity check before inserting a class registration
-- =============================================================================
DROP TRIGGER IF EXISTS trg_check_class_capacity ON ClassRegistration;

CREATE TRIGGER trg_check_class_capacity
BEFORE INSERT ON ClassRegistration
FOR EACH ROW
EXECUTE FUNCTION check_class_capacity();

-- =============================================================================
-- INDEXES: Improve query performance
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_classregistration_class_id
ON ClassRegistration (class_id);

CREATE INDEX IF NOT EXISTS idx_ptsession_trainer_start_time
ON PTSession (trainer_id, start_time);

CREATE INDEX IF NOT EXISTS idx_fitnessgoal_member_active
ON FitnessGoal (member_id, is_active);

CREATE INDEX IF NOT EXISTS idx_healthmetric_member_recorded
ON HealthMetric (member_id, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_invoice_member_status
ON Invoice (member_id, status);


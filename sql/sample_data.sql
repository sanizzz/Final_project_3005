-- sample_data.sql
-- DML: INSERT sample data for demonstration

-- =============================================================================
-- Members
-- =============================================================================
INSERT INTO Member (full_name, email, phone, date_of_birth, gender) VALUES
('Hannah Lee', 'hannah.lee@example.com', '555-0101', '1990-03-15', 'Female'),
('Mohammed Ali', 'mohammed.ali@example.com', '555-0102', '1985-07-22', 'Male'),
('Sara Patel', 'sara.patel@example.com', '555-0103', '1992-11-08', 'Female'),
('Jason Kim', 'jason.kim@example.com', '555-0104', '1988-01-30', 'Male'),
('Emily Chen', 'emily.chen@example.com', '555-0105', '1995-06-12', 'Female');

-- =============================================================================
-- Trainers
-- =============================================================================
INSERT INTO Trainer (full_name, email, specialty) VALUES
('Alex Johnson', 'alex.johnson@gym.com', 'Strength Training'),
('Bella Singh', 'bella.singh@gym.com', 'Yoga & Flexibility'),
('Carlos Ramirez', 'carlos.ramirez@gym.com', 'Cardio & HIIT');

-- =============================================================================
-- Rooms
-- =============================================================================
INSERT INTO Room (name, capacity) VALUES
('Main Studio', 30),
('Yoga Room', 20),
('Weight Room', 15);

-- =============================================================================
-- Fitness Classes
-- =============================================================================
INSERT INTO FitnessClass (title, description, trainer_id, room_id, start_time, end_time, max_capacity) VALUES
('Morning Yoga', 'Start your day with relaxing yoga poses', 2, 2, '2025-01-06 07:00:00', '2025-01-06 08:00:00', 20),
('HIIT Blast', 'High intensity interval training for all levels', 3, 1, '2025-01-06 12:00:00', '2025-01-06 13:00:00', 25);

-- =============================================================================
-- Class Registrations
-- =============================================================================
INSERT INTO ClassRegistration (member_id, class_id, registered_at) VALUES
(1, 1, '2025-01-01 10:00:00'),
(2, 1, '2025-01-01 11:30:00'),
(3, 2, '2025-01-02 09:00:00');

-- =============================================================================
-- PT Sessions
-- =============================================================================
INSERT INTO PTSession (member_id, trainer_id, room_id, start_time, end_time, status) VALUES
(1, 1, 3, '2025-01-07 10:00:00', '2025-01-07 11:00:00', 'BOOKED'),
(4, 3, 1, '2025-01-07 14:00:00', '2025-01-07 15:00:00', 'BOOKED');

-- =============================================================================
-- Fitness Goals
-- =============================================================================
INSERT INTO FitnessGoal (member_id, goal_type, target_value, start_date, target_date, is_active) VALUES
(1, 'Weight Loss', 65.0, '2025-01-01', '2025-04-01', TRUE),
(2, 'Build Muscle', 80.0, '2025-01-01', '2025-06-01', TRUE),
(3, 'Run 5K', 25.0, '2025-01-01', '2025-03-01', TRUE),
(4, 'Flexibility', 10.0, '2025-01-01', '2025-02-01', FALSE);

-- =============================================================================
-- Health Metrics
-- =============================================================================
INSERT INTO HealthMetric (member_id, recorded_at, weight_kg, heart_rate_bpm, body_fat_percent) VALUES
(1, '2025-01-01 08:00:00', 70.5, 72, 22.5),
(1, '2025-01-15 08:00:00', 69.8, 70, 22.0),
(2, '2025-01-01 09:00:00', 75.0, 68, 18.0),
(3, '2025-01-02 07:30:00', 58.0, 65, 20.0);

-- =============================================================================
-- Trainer Availability
-- =============================================================================
INSERT INTO TrainerAvailability (trainer_id, start_time, end_time) VALUES
(1, '2025-01-06 09:00:00', '2025-01-06 17:00:00'),
(1, '2025-01-07 09:00:00', '2025-01-07 17:00:00'),
(2, '2025-01-06 06:00:00', '2025-01-06 14:00:00'),
(3, '2025-01-06 10:00:00', '2025-01-06 18:00:00');

-- =============================================================================
-- Invoices
-- =============================================================================
INSERT INTO Invoice (member_id, amount, description, issued_at, due_at, status) VALUES
(1, 99.99, 'Monthly Membership - January', '2025-01-01 00:00:00', '2025-01-15 00:00:00', 'PAID'),
(2, 99.99, 'Monthly Membership - January', '2025-01-01 00:00:00', '2025-01-15 00:00:00', 'UNPAID'),
(1, 50.00, 'Personal Training Session', '2025-01-05 00:00:00', '2025-01-20 00:00:00', 'UNPAID');


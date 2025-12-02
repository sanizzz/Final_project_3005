-- schema.sql
-- DDL: CREATE TABLE statements for Health & Fitness Club Management System

CREATE TABLE IF NOT EXISTS Member (
    member_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    full_name TEXT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    date_of_birth DATE,
    gender TEXT
);

CREATE TABLE IF NOT EXISTS Trainer (
    trainer_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    full_name TEXT,
    email TEXT UNIQUE NOT NULL,
    specialty TEXT
);

CREATE TABLE IF NOT EXISTS Room (
    room_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT,
    capacity INTEGER
);

CREATE TABLE IF NOT EXISTS FitnessClass (
    class_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    title TEXT,
    description TEXT,
    trainer_id BIGINT REFERENCES Trainer(trainer_id),
    room_id BIGINT REFERENCES Room(room_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    max_capacity INTEGER
);

CREATE TABLE IF NOT EXISTS ClassRegistration (
    registration_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    member_id BIGINT REFERENCES Member(member_id),
    class_id BIGINT REFERENCES FitnessClass(class_id),
    registered_at TIMESTAMP,
    UNIQUE (member_id, class_id)
);

CREATE TABLE IF NOT EXISTS PTSession (
    session_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    member_id BIGINT REFERENCES Member(member_id),
    trainer_id BIGINT REFERENCES Trainer(trainer_id),
    room_id BIGINT REFERENCES Room(room_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT
);

CREATE TABLE IF NOT EXISTS FitnessGoal (
    goal_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    member_id BIGINT REFERENCES Member(member_id),
    goal_type TEXT,
    target_value NUMERIC,
    start_date DATE,
    target_date DATE,
    is_active BOOLEAN
);

CREATE TABLE IF NOT EXISTS HealthMetric (
    metric_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    member_id BIGINT REFERENCES Member(member_id),
    recorded_at TIMESTAMP,
    weight_kg NUMERIC,
    heart_rate_bpm INTEGER,
    body_fat_percent NUMERIC
);

CREATE TABLE IF NOT EXISTS TrainerAvailability (
    availability_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    trainer_id BIGINT REFERENCES Trainer(trainer_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Invoice (
    invoice_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    member_id BIGINT REFERENCES Member(member_id),
    amount NUMERIC,
    description TEXT,
    issued_at TIMESTAMP,
    due_at TIMESTAMP,
    status TEXT
);


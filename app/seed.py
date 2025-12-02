"""Seeder that loads a substantive dataset for video demos."""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from models import (
    ClassRegistration,
    FitnessClass,
    FitnessGoal,
    HealthMetric,
    Invoice,
    Member,
    PTSession,
    Room,
    Trainer,
    TrainerAvailability,
)


def seed_data(session: Session) -> None:
    """Insert a full set of demo data covering every table."""
    if session.query(Member).first():
        print("Sample data already exists, skipping seed.")
        return

    random.seed(42)
    base_datetime = datetime.now().replace(minute=0, second=0, microsecond=0)

    rooms = [
        Room(name=f"Studio {i}", capacity=20 + (i % 10))
        for i in range(1, 26)
    ]
    session.add_all(rooms)
    session.flush()

    trainers = [
        Trainer(
            full_name=f"Trainer {i}",
            email=f"trainer{i}@club.com",
            specialty=random.choice(["Yoga", "Strength", "Cardio", "Pilates"]),
        )
        for i in range(1, 26)
    ]
    session.add_all(trainers)
    session.flush()

    members = []
    for i in range(1, 41):
        members.append(
            Member(
                full_name=f"Member {i}",
                email=f"member{i}@example.com",
                phone=f"555-01{i:02d}",
                date_of_birth=date(1985 + (i % 10), (i % 12) + 1, (i % 27) + 1),
                gender="Female" if i % 2 == 0 else "Male",
            )
        )
    session.add_all(members)
    session.flush()

    availability_entries = []
    for idx, trainer in enumerate(trainers):
        for slot in range(2):
            start = base_datetime + timedelta(days=(idx + slot) % 7, hours=6 + slot * 4)
            availability_entries.append(
                TrainerAvailability(
                    trainer_id=trainer.id,
                    start_time=start,
                    end_time=start + timedelta(hours=3),
                )
            )
    session.add_all(availability_entries)

    classes = []
    for i in range(30):
        trainer = trainers[i % len(trainers)]
        room = rooms[i % len(rooms)]
        start = base_datetime + timedelta(days=i // 3, hours=6 + (i % 3) * 2)
        end = start + timedelta(hours=1)
        max_capacity = min(room.capacity, 10 + (i % 4) * 5)
        classes.append(
            FitnessClass(
                title=f"Class {i + 1}",
                description=f"High energy session #{i + 1}",
                start_time=start,
                end_time=end,
                max_capacity=max_capacity,
                trainer_id=trainer.id,
                room_id=room.id,
            )
        )
    session.add_all(classes)
    session.flush()

    goals = []
    for member in members:
        for j in range(12):
            start_date = date.today() - timedelta(days=120 - j * 5)
            goals.append(
                FitnessGoal(
                    member_id=member.id,
                    goal_type=f"Goal {j + 1}",
                    target_value=70.0 + j,
                    start_date=start_date,
                    target_date=start_date + timedelta(days=60),
                    is_active=True,
                )
            )
    session.add_all(goals)

    metrics = []
    for member in members[:15]:
        for j in range(12):
            recorded_at = base_datetime - timedelta(days=j * 7)
            metrics.append(
                HealthMetric(
                    member_id=member.id,
                    recorded_at=recorded_at,
                    weight_kg=80 - j,
                    heart_rate_bpm=70 + (j % 6),
                    body_fat_percent=25 - j * 0.2,
                )
            )
    session.add_all(metrics)

    pt_sessions = []
    for i in range(24):
        member = members[i % len(members)]
        trainer = trainers[i % len(trainers)]
        room = rooms[(i + 3) % len(rooms)]
        start = base_datetime + timedelta(days=i, hours=14)
        pt_sessions.append(
            PTSession(
                member_id=member.id,
                trainer_id=trainer.id,
                room_id=room.id,
                start_time=start,
                end_time=start + timedelta(hours=1),
                status="COMPLETED" if i % 4 == 0 else "BOOKED",
            )
        )
    session.add_all(pt_sessions)

    invoices = []
    for i, member in enumerate(members[:30], start=1):
        invoices.append(
            Invoice(
                member_id=member.id,
                amount=50.0 + (i % 6) * 5,
                description=f"Invoice #{i}",
                due_at=base_datetime + timedelta(days=30),
                status="PAID" if i % 3 == 0 else "UNPAID",
            )
        )
    session.add_all(invoices)

    registrations = []
    for class_obj in classes[:5]:
        capacity = class_obj.max_capacity
        for member in members[:capacity]:
            registrations.append(
                ClassRegistration(member_id=member.id, class_id=class_obj.id)
            )
    session.add_all(registrations)

    session.commit()
    print("Sample data inserted.")

"""All ORM models live in this single module to keep the project simple."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column("member_id", primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(20))

    goals: Mapped[List["FitnessGoal"]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )
    health_metrics: Mapped[List["HealthMetric"]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )
    pt_sessions: Mapped[List["PTSession"]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )
    class_registrations: Mapped[List["ClassRegistration"]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )


class Trainer(Base):
    __tablename__ = "trainer"

    id: Mapped[int] = mapped_column("trainer_id", primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    specialty: Mapped[Optional[str]] = mapped_column(String(200))

    pt_sessions: Mapped[List["PTSession"]] = relationship(back_populates="trainer")
    classes: Mapped[List["FitnessClass"]] = relationship(back_populates="trainer")
    availability_slots: Mapped[List["TrainerAvailability"]] = relationship(
        back_populates="trainer"
    )


class Room(Base):
    __tablename__ = "room"

    id: Mapped[int] = mapped_column("room_id", primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)

    classes: Mapped[List["FitnessClass"]] = relationship(back_populates="room")
    pt_sessions: Mapped[List["PTSession"]] = relationship(back_populates="room")


class FitnessClass(Base):
    __tablename__ = "fitnessclass"

    id: Mapped[int] = mapped_column("class_id", primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainer.trainer_id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.room_id"), nullable=False)

    trainer: Mapped["Trainer"] = relationship(back_populates="classes")
    room: Mapped["Room"] = relationship(back_populates="classes")
    registrations: Mapped[List["ClassRegistration"]] = relationship(
        back_populates="fitness_class"
    )


class ClassRegistration(Base):
    __tablename__ = "classregistration"
    __table_args__ = (UniqueConstraint("member_id", "class_id", name="uq_member_class"),)

    id: Mapped[int] = mapped_column("registration_id", primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.member_id"), nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("fitnessclass.class_id"), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    member: Mapped["Member"] = relationship(back_populates="class_registrations")
    fitness_class: Mapped["FitnessClass"] = relationship(back_populates="registrations")


class PTSession(Base):
    __tablename__ = "ptsession"

    id: Mapped[int] = mapped_column("session_id", primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.member_id"), nullable=False)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainer.trainer_id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.room_id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="BOOKED")

    member: Mapped["Member"] = relationship(back_populates="pt_sessions")
    trainer: Mapped["Trainer"] = relationship(back_populates="pt_sessions")
    room: Mapped["Room"] = relationship(back_populates="pt_sessions")


class FitnessGoal(Base):
    __tablename__ = "fitnessgoal"

    id: Mapped[int] = mapped_column("goal_id", primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.member_id"), nullable=False)
    goal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    member: Mapped["Member"] = relationship(back_populates="goals")


class HealthMetric(Base):
    __tablename__ = "healthmetric"

    id: Mapped[int] = mapped_column("metric_id", primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.member_id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    heart_rate_bpm: Mapped[Optional[int]] = mapped_column(Integer)
    body_fat_percent: Mapped[Optional[float]] = mapped_column(Float)

    member: Mapped["Member"] = relationship(back_populates="health_metrics")


class TrainerAvailability(Base):
    __tablename__ = "traineravailability"

    id: Mapped[int] = mapped_column("availability_id", primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainer.trainer_id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    trainer: Mapped["Trainer"] = relationship(back_populates="availability_slots")


class Invoice(Base):
    __tablename__ = "invoice"

    id: Mapped[int] = mapped_column("invoice_id", primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.member_id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    issued_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="UNPAID")

    member: Mapped["Member"] = relationship(back_populates="invoices")


__all__ = [
    "Base",
    "Member",
    "Trainer",
    "Room",
    "FitnessClass",
    "ClassRegistration",
    "PTSession",
    "FitnessGoal",
    "HealthMetric",
    "TrainerAvailability",
    "Invoice",
]

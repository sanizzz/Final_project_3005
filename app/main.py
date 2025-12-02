"""Text CLI for the Health & Fitness Club Management System."""

from __future__ import annotations

from datetime import date, datetime
from typing import Callable, Optional

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
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
from app.db import get_session, init_db
from app.seed import seed_data

DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %H:%M"


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------
def prompt_required(message: str) -> str:
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Value is required.")


def prompt_optional(message: str) -> Optional[str]:
    value = input(message).strip()
    return value or None


def prompt_int(message: str) -> int:
    while True:
        value = input(message).strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid integer.")


def prompt_int_with_default(message: str, current: int) -> int:
    while True:
        value = input(message).strip()
        if not value:
            return current
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid integer.")


def prompt_float(message: str, allow_blank: bool = False) -> Optional[float]:
    while True:
        value = input(message).strip()
        if not value and allow_blank:
            return None
        try:
            return float(value)
        except ValueError:
            print("Please enter a number.")


def prompt_date(message: str, allow_blank: bool = True) -> Optional[date]:
    while True:
        value = input(message).strip()
        if not value and allow_blank:
            return None
        try:
            return datetime.strptime(value, DATE_FMT).date()
        except ValueError:
            print(f"Use format {DATE_FMT}.")


def prompt_datetime(message: str) -> datetime:
    while True:
        value = input(message).strip()
        try:
            return datetime.strptime(value, DATETIME_FMT)
        except ValueError:
            print(f"Use format {DATETIME_FMT}.")


def prompt_datetime_with_default(message: str, current: datetime) -> datetime:
    while True:
        value = input(message).strip()
        if not value:
            return current
        try:
            return datetime.strptime(value, DATETIME_FMT)
        except ValueError:
            print(f"Use format {DATETIME_FMT}.")


# ---------------------------------------------------------------------------
# Small utility helpers
# ---------------------------------------------------------------------------
def trainer_has_conflict(
    session: Session,
    trainer_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_class_id: Optional[int] = None,
    exclude_session_id: Optional[int] = None,
) -> bool:
    class_stmt = select(FitnessClass.id).where(
        FitnessClass.trainer_id == trainer_id,
        FitnessClass.start_time < end_time,
        FitnessClass.end_time > start_time,
    )
    if exclude_class_id:
        class_stmt = class_stmt.where(FitnessClass.id != exclude_class_id)

    session_stmt = select(PTSession.id).where(
        PTSession.trainer_id == trainer_id,
        PTSession.start_time < end_time,
        PTSession.end_time > start_time,
    )
    if exclude_session_id:
        session_stmt = session_stmt.where(PTSession.id != exclude_session_id)

    return bool(session.scalar(class_stmt) or session.scalar(session_stmt))


def room_has_conflict(
    session: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_class_id: Optional[int] = None,
    exclude_session_id: Optional[int] = None,
) -> bool:
    class_stmt = select(FitnessClass.id).where(
        FitnessClass.room_id == room_id,
        FitnessClass.start_time < end_time,
        FitnessClass.end_time > start_time,
    )
    if exclude_class_id:
        class_stmt = class_stmt.where(FitnessClass.id != exclude_class_id)

    session_stmt = select(PTSession.id).where(
        PTSession.room_id == room_id,
        PTSession.start_time < end_time,
        PTSession.end_time > start_time,
    )
    if exclude_session_id:
        session_stmt = session_stmt.where(PTSession.id != exclude_session_id)

    return bool(session.scalar(class_stmt) or session.scalar(session_stmt))


# ---------------------------------------------------------------------------
# Member operations
# ---------------------------------------------------------------------------
def register_member() -> None:
    print("\n--- Register New Member ---")
    full_name = prompt_required("Full name: ")
    email = prompt_required("Email: ")
    phone = prompt_optional("Phone (optional): ")
    dob = prompt_date(f"Date of birth ({DATE_FMT}) (optional): ")
    gender = prompt_optional("Gender (optional): ")

    with get_session() as session:
        try:
            existing = session.scalar(select(Member).where(Member.email == email))
            if existing:
                print("Another member already uses that email.")
                return

            session.add(
                Member(
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    date_of_birth=dob,
                    gender=gender,
                )
            )
            session.commit()
            print("Member registered successfully.")
        except Exception as exc:
            session.rollback()
            print(f"Failed to register member: {exc}")


def update_profile_and_goal() -> None:
    print("\n--- Update Profile and Goal ---")
    member_id = prompt_int("Member id: ")

    with get_session() as session:
        member = session.get(Member, member_id)
        if not member:
            print("Member not found.")
            return

        new_name = prompt_optional(f"Full name ({member.full_name}): ")
        new_phone = prompt_optional(f"Phone ({member.phone or 'None'}): ")
        new_gender = prompt_optional(f"Gender ({member.gender or 'None'}): ")

        if new_name:
            member.full_name = new_name
        if new_phone is not None:
            member.phone = new_phone
        if new_gender is not None:
            member.gender = new_gender

        goal_type = prompt_required("Goal type: ")
        target_value = prompt_float("Target value: ")
        start_date = prompt_date(f"Start date ({DATE_FMT}): ", allow_blank=False)
        target_date = prompt_date(f"Target date ({DATE_FMT}): ", allow_blank=False)

        if start_date and target_date and target_date < start_date:
            print("Target date must be after start date.")
            session.rollback()
            return

        for goal in member.goals:
            goal.is_active = False

        session.add(
            FitnessGoal(
                member_id=member.id,
                goal_type=goal_type,
                target_value=target_value or 0.0,
                start_date=start_date or date.today(),
                target_date=target_date or date.today(),
                is_active=True,
            )
        )
        session.commit()
        print("Profile and goal updated.")


def add_health_metric() -> None:
    print("\n--- Add Health Metric ---")
    member_id = prompt_int("Member id: ")
    weight = prompt_float("Weight (kg, optional): ", allow_blank=True)
    heart_rate = prompt_float("Heart rate (bpm, optional): ", allow_blank=True)
    body_fat = prompt_float("Body fat % (optional): ", allow_blank=True)

    with get_session() as session:
        member = session.get(Member, member_id)
        if not member:
            print("Member not found.")
            return
        session.add(
            HealthMetric(
                member_id=member.id,
                weight_kg=weight,
                heart_rate_bpm=int(heart_rate) if heart_rate is not None else None,
                body_fat_percent=body_fat,
                recorded_at=datetime.now(),
            )
        )
        session.commit()
        print("Metric recorded.")


def register_for_class() -> None:
    print("\n--- Register for Class ---")
    member_id = prompt_int("Member id: ")
    class_id = prompt_int("Class id: ")

    with get_session() as session:
        member = session.get(Member, member_id)
        fitness_class = session.get(FitnessClass, class_id)
        if not member or not fitness_class:
            print("Member or class not found.")
            return

        existing = session.scalar(
            select(ClassRegistration).where(
                ClassRegistration.member_id == member_id,
                ClassRegistration.class_id == class_id,
            )
        )
        if existing:
            print("Member already registered for this class.")
            return

        session.add(ClassRegistration(member_id=member_id, class_id=class_id))
        try:
            session.commit()
            print("Registration completed.")
        except IntegrityError as exc:
            session.rollback()
            message = str(getattr(exc, "orig", exc)).lower()
            if "class" in message and "full" in message:
                print("Registration failed: the class is full (trigger enforced).")
            else:
                print(f"Registration failed: {exc}")
        except Exception as exc:
            session.rollback()
            print(f"Registration failed: {exc}")


# ---------------------------------------------------------------------------
# Trainer operations
# ---------------------------------------------------------------------------
def set_trainer_availability() -> None:
    print("\n--- Set Trainer Availability ---")
    trainer_id = prompt_int("Trainer id: ")
    start_time = prompt_datetime(f"Start time ({DATETIME_FMT}): ")
    end_time = prompt_datetime(f"End time ({DATETIME_FMT}): ")

    if end_time <= start_time:
        print("End time must be after start time.")
        return

    with get_session() as session:
        trainer = session.get(Trainer, trainer_id)
        if not trainer:
            print("Trainer not found.")
            return

        overlap = session.scalar(
            select(TrainerAvailability).where(
                TrainerAvailability.trainer_id == trainer_id,
                TrainerAvailability.start_time < end_time,
                TrainerAvailability.end_time > start_time,
            )
        )
        if overlap:
            print("Slot overlaps with an existing availability entry.")
            return

        session.add(
            TrainerAvailability(
                trainer_id=trainer_id, start_time=start_time, end_time=end_time
            )
        )
        session.commit()
        print("Availability saved.")


def view_trainer_schedule() -> None:
    print("\n--- Trainer Schedule ---")
    trainer_id = prompt_int("Trainer id: ")
    now = datetime.now()

    with get_session() as session:
        trainer = session.get(Trainer, trainer_id)
        if not trainer:
            print("Trainer not found.")
            return

        pt_sessions = session.scalars(
            select(PTSession)
            .where(PTSession.trainer_id == trainer_id, PTSession.start_time >= now)
            .order_by(PTSession.start_time)
        ).all()
        classes = session.scalars(
            select(FitnessClass)
            .where(FitnessClass.trainer_id == trainer_id, FitnessClass.start_time >= now)
            .order_by(FitnessClass.start_time)
        ).all()

        print(f"\nUpcoming PT Sessions for {trainer.full_name}:")
        if not pt_sessions:
            print("  (none)")
        for session_item in pt_sessions:
            print(
                f"  Session #{session_item.id} with member {session_item.member_id} "
                f"{session_item.start_time:%Y-%m-%d %H:%M} - {session_item.end_time:%H:%M}"
            )

        print(f"\nUpcoming Classes for {trainer.full_name}:")
        if not classes:
            print("  (none)")
        for cls in classes:
            print(
                f"  Class #{cls.id} '{cls.title}' in room {cls.room_id} "
                f"{cls.start_time:%Y-%m-%d %H:%M} - {cls.end_time:%H:%M}"
            )


def lookup_member_info() -> None:
    print("\n--- Lookup Member ---")
    query = prompt_required("Enter part of a member name: ")

    with get_session() as session:
        members = session.scalars(
            select(Member).where(Member.full_name.ilike(f"%{query}%")).order_by(Member.full_name)
        ).all()
        if not members:
            print("No members found.")
            return

        for member in members:
            goal = session.scalar(
                select(FitnessGoal)
                .where(FitnessGoal.member_id == member.id, FitnessGoal.is_active.is_(True))
                .order_by(FitnessGoal.id.desc())
            )
            metric = session.scalar(
                select(HealthMetric)
                .where(HealthMetric.member_id == member.id)
                .order_by(HealthMetric.recorded_at.desc())
            )
            goal_desc = (
                f"{goal.goal_type} → {goal.target_value}" if goal else "No active goal"
            )
            if metric:
                metric_desc = f"Weight {metric.weight_kg}kg, HR {metric.heart_rate_bpm}"
            else:
                metric_desc = "No recent metrics"
            print(f"- {member.full_name} (#{member.id}) | {goal_desc} | {metric_desc}")


# ---------------------------------------------------------------------------
# Admin operations
# ---------------------------------------------------------------------------
def manage_fitness_class() -> None:
    print("\n--- Manage Fitness Class ---")
    action = prompt_required("Create or update? (C/U): ").upper()
    if action not in {"C", "U"}:
        print("Invalid choice.")
        return

    with get_session() as session:
        if action == "C":
            title = prompt_required("Title: ")
            description = prompt_optional("Description: ")
            trainer_id = prompt_int("Trainer id: ")
            room_id = prompt_int("Room id: ")
            start_time = prompt_datetime(f"Start time ({DATETIME_FMT}): ")
            end_time = prompt_datetime(f"End time ({DATETIME_FMT}): ")
            max_capacity = prompt_int("Max capacity: ")

            if end_time <= start_time:
                print("End time must be after start time.")
                return

            trainer = session.get(Trainer, trainer_id)
            room = session.get(Room, room_id)
            if not trainer or not room:
                print("Trainer or room not found.")
                return
            if max_capacity > room.capacity:
                print("Max capacity cannot exceed the room capacity.")
                return

            if trainer_has_conflict(session, trainer_id, start_time, end_time):
                print("Trainer already has a booking in that window.")
                return
            if room_has_conflict(session, room_id, start_time, end_time):
                print("Room already booked in that window.")
                return

            fitness_class = FitnessClass(
                title=title,
                description=description,
                trainer_id=trainer_id,
                room_id=room_id,
                start_time=start_time,
                end_time=end_time,
                max_capacity=max_capacity,
            )
            session.add(fitness_class)
            session.commit()
            print(f"Fitness class created with id {fitness_class.id}.")
            return

        class_id = prompt_int("Class id to update: ")
        fitness_class = session.get(FitnessClass, class_id)
        if not fitness_class:
            print("Class not found.")
            return

        new_title = prompt_optional(f"Title ({fitness_class.title}): ")
        new_description = prompt_optional(
            f"Description ({fitness_class.description or 'None'}): "
        )
        trainer_id = prompt_int_with_default(
            f"Trainer id ({fitness_class.trainer_id}): ", fitness_class.trainer_id
        )
        room_id = prompt_int_with_default(
            f"Room id ({fitness_class.room_id}): ", fitness_class.room_id
        )
        start_time = prompt_datetime_with_default(
            f"Start time ({fitness_class.start_time:%Y-%m-%d %H:%M}): ",
            fitness_class.start_time,
        )
        end_time = prompt_datetime_with_default(
            f"End time ({fitness_class.end_time:%Y-%m-%d %H:%M}): ",
            fitness_class.end_time,
        )
        max_capacity = prompt_int_with_default(
            f"Max capacity ({fitness_class.max_capacity}): ",
            fitness_class.max_capacity,
        )

        trainer = session.get(Trainer, trainer_id)
        room = session.get(Room, room_id)
        if not trainer or not room:
            print("Trainer or room not found.")
            return
        if max_capacity > room.capacity:
            print("Max capacity cannot exceed the room capacity.")
            return
        if end_time <= start_time:
            print("End time must be after start time.")
            return

        if trainer_has_conflict(
            session, trainer_id, start_time, end_time, exclude_class_id=fitness_class.id
        ):
            print("Trainer already has a booking in that window.")
            return
        if room_has_conflict(
            session, room_id, start_time, end_time, exclude_class_id=fitness_class.id
        ):
            print("Room already booked in that window.")
            return

        if new_title:
            fitness_class.title = new_title
        if new_description is not None:
            fitness_class.description = new_description
        fitness_class.trainer_id = trainer_id
        fitness_class.room_id = room_id
        fitness_class.start_time = start_time
        fitness_class.end_time = end_time
        fitness_class.max_capacity = max_capacity
        session.commit()
        print("Class updated.")


def schedule_pt_session() -> None:
    print("\n--- Schedule PT Session ---")
    member_id = prompt_int("Member id: ")
    trainer_id = prompt_int("Trainer id: ")
    room_id = prompt_int("Room id: ")
    start_time = prompt_datetime(f"Start time ({DATETIME_FMT}): ")
    end_time = prompt_datetime(f"End time ({DATETIME_FMT}): ")

    if end_time <= start_time:
        print("End time must be after start time.")
        return

    with get_session() as session:
        member = session.get(Member, member_id)
        trainer = session.get(Trainer, trainer_id)
        room = session.get(Room, room_id)
        if not all([member, trainer, room]):
            print("Invalid member, trainer, or room id.")
            return

        if trainer_has_conflict(session, trainer_id, start_time, end_time):
            print("Trainer already booked.")
            return
        if room_has_conflict(session, room_id, start_time, end_time):
            print("Room already booked.")
            return

        pt_session = PTSession(
            member_id=member_id,
            trainer_id=trainer_id,
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
            status="BOOKED",
        )
        session.add(pt_session)
        session.commit()
        print(f"PT session scheduled with id {pt_session.id}.")


def create_and_pay_invoice() -> None:
    print("\n--- Invoice Management ---")
    action = prompt_required("Create invoice or mark paid? (C/P): ").upper()
    if action not in {"C", "P"}:
        print("Invalid choice.")
        return

    with get_session() as session:
        if action == "P":
            invoice_id = prompt_int("Invoice id to mark paid: ")
            invoice = session.get(Invoice, invoice_id)
            if not invoice:
                print("Invoice not found.")
                return
            invoice.status = "PAID"
            invoice.due_at = invoice.due_at or datetime.now()
            session.commit()
            print("Invoice marked as paid.")
            return

        member_id = prompt_int("Member id: ")
        amount = prompt_float("Amount: ")
        description = prompt_optional("Description: ")

        member = session.get(Member, member_id)
        if not member:
            print("Member not found.")
            return

        invoice = Invoice(
            member_id=member_id,
            amount=amount or 0.0,
            description=description,
            status="UNPAID",
        )
        session.add(invoice)
        mark_paid = prompt_optional("Mark as paid immediately? (y/n): ")
        if mark_paid and mark_paid.lower().startswith("y"):
            invoice.status = "PAID"
            invoice.due_at = datetime.now()
        session.commit()
        print(f"Invoice created with id {invoice.id}.")


def view_member_dashboard() -> None:
    print("\n--- Member Dashboard ---")
    member_id = prompt_int("Member id: ")

    with get_session() as session:
        result = session.execute(
            text(
                """
                SELECT member_id, full_name, email, phone, goal_type,
                       target_value, target_date, latest_metric_at,
                       weight_kg, heart_rate_bpm, body_fat_percent
                FROM member_dashboard_view
                WHERE member_id = :member_id
                """
            ),
            {"member_id": member_id},
        ).mappings().first()

        if not result:
            print("No information available for that member.")
            return

        print(f"\nMember #{result['member_id']}: {result['full_name']} ({result['email']})")
        print(f"Phone: {result['phone'] or 'N/A'}")
        goal_desc = "No active goal"
        if result["goal_type"]:
            target_date = (
                f"{result['target_date']:%Y-%m-%d}"
                if result["target_date"]
                else "unspecified date"
            )
            goal_desc = f"{result['goal_type']} target {result['target_value']} by {target_date}"
        print(f"Active goal: {goal_desc}")
        if result["latest_metric_at"]:
            metric_time = result["latest_metric_at"]
            print(
                f"Latest metric ({metric_time:%Y-%m-%d %H:%M}): "
                f"weight {result['weight_kg'] or 'N/A'}kg, "
                f"HR {result['heart_rate_bpm'] or 'N/A'}, "
                f"body fat {result['body_fat_percent'] or 'N/A'}%"
            )
        else:
            print("No recorded health metrics yet.")


# ---------------------------------------------------------------------------
# Menus and entry point
# ---------------------------------------------------------------------------
def member_menu() -> None:
    actions: dict[str, Callable[[], None]] = {
        "1": register_member,
        "2": update_profile_and_goal,
        "3": add_health_metric,
        "4": register_for_class,
        "5": view_member_dashboard,
    }
    while True:
        print(
            "\nMember Menu\n"
            "1) Register new member\n"
            "2) Update profile & active goal\n"
            "3) Add health metric\n"
            "4) Register for group class\n"
            "5) View dashboard summary\n"
            "9) Back to main menu"
        )
        choice = input("Select an option: ").strip()
        if choice == "9":
            return
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


def trainer_menu() -> None:
    actions: dict[str, Callable[[], None]] = {
        "1": set_trainer_availability,
        "2": view_trainer_schedule,
        "3": lookup_member_info,
    }
    while True:
        print(
            "\nTrainer Menu\n"
            "1) Set availability slot\n"
            "2) View my schedule\n"
            "3) Lookup member info\n"
            "9) Back to main menu"
        )
        choice = input("Select an option: ").strip()
        if choice == "9":
            return
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


def admin_menu() -> None:
    actions: dict[str, Callable[[], None]] = {
        "1": manage_fitness_class,
        "2": schedule_pt_session,
        "3": create_and_pay_invoice,
    }
    while True:
        print(
            "\nAdmin Menu\n"
            "1) Create or update group class\n"
            "2) Schedule PT session\n"
            "3) Create and pay invoice\n"
            "9) Back to main menu"
        )
        choice = input("Select an option: ").strip()
        if choice == "9":
            return
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


def main() -> None:
    print("Setting up database...")
    init_db()
    seed_choice = input("Seed sample data? (y/n): ").strip().lower()
    if seed_choice == "y":
        with get_session() as session:
            try:
                seed_data(session)
            except Exception as exc:
                session.rollback()
                print(f"Seeding failed: {exc}")

    while True:
        print(
            "\nHealth & Fitness Club Management System\n"
            "1) Member menu\n"
            "2) Trainer menu\n"
            "3) Admin menu\n"
            "9) Quit"
        )
        choice = input("Select an option: ").strip()
        if choice == "9":
            print("Goodbye!")
            break
        if choice == "1":
            member_menu()
        elif choice == "2":
            trainer_menu()
        elif choice == "3":
            admin_menu()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()

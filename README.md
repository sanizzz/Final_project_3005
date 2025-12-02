# Health & Fitness Club Management System
Sanidhya Khanna (101307214)
Dhirran Pirabaharan (101244401)

This repository contains our final project for **[COURSE CODE]** at **[UNIVERSITY]**.  
We designed a **PostgreSQL** database and a **CLI-based application** to manage a health & fitness club, including:

- Members and their fitness goals  
- Trainers, rooms, and group classes  
- Personal training (PT) sessions  
- Health metrics (weight, heart rate, body fat)  
- Trainer availability and simple invoices  

The focus is on **database design + SQL features + a working CLI demo**, not a fancy UI.

---

## 1. Features

### 1.1 Database design

We implemented **10 entities**:

- `Member` – club members  
- `Trainer` – trainers and instructors  
- `Room` – physical rooms  
- `FitnessClass` – group classes (e.g., yoga, HIIT)  
- `ClassRegistration` – many-to-many link between members and classes  
- `PTSession` – one-on-one personal training sessions  
- `FitnessGoal` – goals per member (e.g., target weight)  
- `HealthMetric` – time-stamped metrics (weight, heart rate, body fat)  
- `TrainerAvailability` – when a trainer is available for PT  
- `Invoice` – simple billing records  

Key relationships (informally):

- Member 1–M FitnessGoal  
- Member 1–M HealthMetric  
- Member 1–M PTSession  
- Trainer 1–M PTSession  
- Trainer 1–M FitnessClass  
- Room 1–M FitnessClass  
- Room 1–M PTSession  
- Member M–N FitnessClass (via `ClassRegistration`)  
- Trainer 1–M TrainerAvailability  
- Member 1–M Invoice  

The full ER diagram is in **`docs/ERD.pdf`**.

### 1.2 Application (CLI)

The CLI supports the **three roles required by the project**:

#### Member menu
- Register new member  
- Update profile & active fitness goal  
- Add health metric entry  
- Register for a group class (capacity-aware)  
- View member dashboard (via a DB VIEW)

#### Trainer menu
- Set availability slot  
- View trainer schedule (PT sessions + classes)  
- Look up member info (active goal + latest health metrics)

#### Admin menu
- Create or update a group class  
- Schedule a PT session (basic trainer/room conflict checks)  
- Create an invoice and optionally mark it as paid  

All operations execute real SQL against PostgreSQL (through Python code).

### 1.3 Advanced DB features

We implemented:

- **View**: `MemberDashboardView`  
  - Joins `Member`, the active `FitnessGoal`, and the latest `HealthMetric` per member.  
  - Used by the CLI “View member dashboard” option.

- **Trigger**: `trg_check_class_capacity` on `ClassRegistration`  
  - Calls `check_class_capacity()` **BEFORE INSERT**.  
  - Counts existing registrations for a class and compares to `FitnessClass.max_capacity`.  
  - If the class is full, the trigger raises an exception.  
  - The CLI catches this and shows a user-friendly message (“class is full”).

- **Indexes**:
  - `idx_classregistration_class_id` on `ClassRegistration(class_id)` for capacity checks.  
  - `idx_ptsession_trainer_start_time` on `PTSession(trainer_id, start_time)` for trainer schedule/conflict queries.  
  - (Optional) `idx_ptsession_room_start_time` on `PTSession(room_id, start_time)` for room conflicts.

All related SQL is in **`sql/extras.sql`**.

---

## 2. Repository structure

```text
.
├─ README.md
├─ requirements.txt          # Python dependencies
├─ sql/
│   ├─ schema.sql            # CREATE TABLE statements
│   ├─ extras.sql            # VIEW, TRIGGER, INDEX definitions
│   └─ sample_data.sql       # Sample data for demo
├─ models/
│   └─ models.py             # ORM models (if using SQLAlchemy)
├─ app/
│   ├─ db.py                 # DB connection, engine, session factory, init_db()
│   ├─ seed.py               # seed_data(session): inserts sample data
│   └─ main.py               # CLI menus + 10+ DB operations
└─ docs/
    ├─ ERD.pdf               # ER diagram
    └─ ProjectReport.pdf     # (optional) project design / write-up

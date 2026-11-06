# Restaurant Reservation Management System

## 1. Project Overview

This project is a Python desktop application for managing restaurant tables and reservations.

It currently uses:

- **Python** for application logic
- **Tkinter / ttk** for the graphical user interface
- **MySQL** for persistent storage of tables and reservations
- **JSON** (`business_data.json`) for basic restaurant configuration and table information

The application is intended to help restaurant staff view tables, create and manage reservations, and maintain the restaurant's table list.

> **Project status:** This README describes the project as it currently exists. It does not imply that the known limitations listed below have already been fixed.

## 2. Current Features

### Initial setup

If `business_data.json` does not exist, the application starts the setup process. The setup collects the restaurant name and the initial table names and capacities, then prepares the MySQL database and its tables.

### Main application window

The main window displays the restaurant tables and provides access to reservation and table-management operations.

Tables are represented visually according to their capacity:

- Capacity below 4: circular representation
- Capacity equal to 4: square representation
- Capacity above 4: rectangular representation

The interface also uses table status indicators such as **Busy** and **Free**.

### Reservation management

The current application supports the following reservation operations:

- Create a reservation
- View reservations for a selected date
- Edit an existing reservation
- Cancel a reservation

The reservation form includes:

- Customer name
- Phone number
- Reservation date
- Reservation time
- Number of guests
- Selected table

The application performs basic input validation, including checks for required names, phone-number format when supplied, past dates/times, positive guest counts, and table selection.

### Table management

The application includes options to:

- Add a table, including its name and capacity
- Remove a table

Table information is currently stored in both MySQL and `business_data.json`.

### Automatic status updates

The `update_status()` function periodically checks reservation information and updates the visual status of tables. It also contains logic for handling old reservations.

The current implementation of this functionality needs further work; see the Known Issues section.

## 3. Project Structure

```text
restaurant-main/
│
├── main.py
├── setup.py
├── create_db.py
├── create_tables.py
├── table_managment.py
├── business_data.json
└── README.md
```

| File | Current responsibility |
|---|---|
| `main.py` | Main Tkinter application, reservation workflows, table display, database operations and status updates |
| `setup.py` | First-run setup, collection of restaurant/table details and database preparation |
| `create_db.py` | Creates the MySQL database if it does not already exist |
| `create_tables.py` | Creates the `Tables` and `Reservations` database tables |
| `table_managment.py` | Present in the project, but currently empty |
| `business_data.json` | Stores restaurant configuration and table information |

## 4. Database Design

The database is named `restaurant`.

### `Tables`

```sql
CREATE TABLE Tables (
    name VARCHAR(10) PRIMARY KEY,
    capacity INT NOT NULL
);
```

| Column | Description |
|---|---|
| `name` | Table identifier/name |
| `capacity` | Maximum number of guests assigned to the table |

### `Reservations`

```sql
CREATE TABLE Reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(10),
    date DATE NOT NULL,
    time TIME NOT NULL,
    people INT NOT NULL,
    FOREIGN KEY (table_name) REFERENCES Tables(name)
);
```

| Column | Description |
|---|---|
| `id` | Unique reservation ID |
| `table_name` | Reserved table |
| `name` | Customer name |
| `phone` | Customer phone number |
| `date` | Reservation date |
| `time` | Reservation time |
| `people` | Number of guests |

## 5. Requirements and Setup

### Requirements

- Python 3
- A running MySQL Server instance
- `mysql-connector-python`
- Tkinter (usually included with standard Python installations; some Linux distributions package it separately)

Install the MySQL connector:

```bash
python -m pip install mysql-connector-python
```

### MySQL configuration

The current code uses local MySQL settings similar to:

```python
host = "localhost"
user = "root"
password = ""
database_name = "restaurant"
```

These settings must match the local MySQL installation. Using a root account without a password is suitable only for a disposable local development environment, not a professional deployment.

### Run the application

From the project directory:

```bash
python main.py
```

If `business_data.json` is missing, the initial setup flow is started. Otherwise, the application attempts to open the main interface.

## 6. Known Issues and Required Improvements

The following items should be addressed before the application is used operationally in a real restaurant.

### Critical reservation logic

1. **No reliable table-capacity validation.** The application does not consistently prevent a reservation from exceeding the selected table's capacity.
2. **No robust double-booking prevention.** Two reservations may be assigned to the same table at overlapping times.
3. **Reservation duration is not modelled explicitly.** Availability needs to be calculated using configurable reservation durations and overlap rules, rather than comparing isolated clock times.
4. **Status calculation needs correction.** The SQL condition in `update_status()` combines `AND` and `OR` in a way that can select records outside the intended date/time range unless grouped correctly.
5. **GUI state may become inconsistent.** `update_status()` may attempt to destroy a button that has not been created.

### Data integrity and database design

6. **Table data is duplicated.** Table information is stored in both MySQL and JSON, which can lead to inconsistent records. MySQL should become the single source of truth for operational data.
7. **Table deletion can fail.** A foreign-key relationship may prevent deleting a table that still has reservations. A clear archival/deactivation policy is preferable to deleting referenced records.
8. **Table-name normalization is inconsistent.** Setup and later table creation do not consistently normalize names (for example, uppercase handling).
9. **Database constraints and transactions need strengthening.** Important rules should be enforced in the application and, where possible, at database level.

### Reliability, security and maintainability

10. **Database credentials are hard-coded.** Credentials should be supplied through environment variables or a protected configuration mechanism.
11. **Error handling needs improvement.** Connection or cursor creation failures may cause additional exceptions during cleanup.
12. **Responsibilities are concentrated in `main.py`.** UI code, SQL, validation and business rules should be separated into maintainable modules.
13. **`table_managment.py` is empty.** Its intended functionality should either be implemented or the unused file removed/renamed.
14. **No dependency lock or requirements file exists.** A `requirements.txt` (or a modern dependency-management configuration) should be added.
15. **No automated test suite exists.** Reservation rules, database operations and important UI workflows need tests.
16. **No authentication or role management exists.** Anyone with access to the application can currently use its management functions.
17. **No backup/restore or export workflow exists.** A professional deployment needs a documented data-protection and recovery process.

## 7. Recommended Professional Architecture

A maintainable version could use a structure such as:

```text
restaurant/
├── app.py
├── config/
│   └── settings.py
├── database/
│   ├── connection.py
│   ├── schema.sql
│   └── repositories/
├── models/
│   ├── table.py
│   └── reservation.py
├── services/
│   ├── reservation_service.py
│   └── table_service.py
├── ui/
│   ├── main_window.py
│   ├── reservations_view.py
│   └── tables_view.py
├── tests/
├── scripts/
├── requirements.txt
└── README.md
```

This is a recommended future structure, not the current structure.

## 8. Professional Implementation Roadmap

### Planning assumptions

The estimate below assumes:

- One experienced Python developer working full-time
- The existing Tkinter desktop application is retained
- MySQL remains the database
- The goal is a reliable application for use by one restaurant location
- The work includes implementation, testing, documentation and deployment preparation
- No major new features such as online customer booking, mobile apps, payment processing or multi-branch support are added

**Estimated duration: 8–10 weeks** for a professional, operational first release. A shorter 4–6 week delivery may be possible for a limited improvement pass, but would involve reduced scope, less hardening or fewer operational features.

### Week-by-week schedule

| Phase | Estimated time | Main work | Deliverable |
|---|---:|---|---|
| 1. Audit and requirements | 3–4 days | Review existing code and workflows, confirm restaurant rules, define reservation duration, opening hours, cancellation and table-availability rules | Requirements and technical plan |
| 2. Database and configuration | 4–5 days | Normalize schema, add migrations, centralize configuration, remove hard-coded credentials, define backup approach | Reliable database foundation |
| 3. Reservation engine | 1–1.5 weeks | Capacity checks, overlapping-reservation prevention, reservation duration, transactions, validation and clear error handling | Tested reservation/business logic |
| 4. Application refactor | 1–1.5 weeks | Separate UI, services, repositories and models; repair table status updates and table-management flows | Maintainable application structure |
| 5. User experience and access control | 4–5 days | Improve forms and feedback, add login and basic roles if required, prevent unsafe operations | More usable and controlled interface |
| 6. Testing and data integrity | 1–1.5 weeks | Unit and integration tests, edge cases, concurrent booking checks, migration and recovery tests | Test report and corrected release candidate |
| 7. Deployment and documentation | 4–5 days | Installation process, dependency list, production configuration, backup/restore instructions, user and technical documentation | Deployable release package |
| 8. Pilot and fixes | 3–5 days | Run realistic restaurant scenarios, collect feedback, fix release-blocking issues | Release 1.0 candidate |

Some tasks can overlap, so the total calendar estimate is approximately **8–10 weeks**, not the sum of every maximum estimate.

### Suggested release milestones

- **End of Week 1:** Requirements agreed and database plan approved.
- **End of Week 3:** Core reservation rules work and are covered by tests.
- **End of Week 5:** Refactored application and table workflows are integrated.
- **End of Week 7:** Main test cycle completed and critical defects resolved.
- **End of Week 8–10:** Pilot, deployment preparation and professional first release.

### Definition of done

The application should not be considered professional-ready until:

- A table cannot be booked for overlapping reservation periods.
- Guest count cannot exceed table capacity unless a documented combination-table feature is implemented.
- Editing a reservation re-checks availability before saving.
- Failed operations do not leave partial or inconsistent database updates.
- Table status is derived consistently from reservation data.
- Database credentials are not committed in source code.
- Important workflows have automated tests.
- Database backup and restore have been tested.
- Installation and configuration are documented.
- The application has been tested using realistic restaurant scenarios.

## 9. Future Features (Not Included in the Estimate)

The following would require additional planning and development:

- Online booking page for customers
- SMS or email reservation confirmations and reminders
- Waitlist management
- Floor-plan editor with drag-and-drop tables
- Reports and analytics
- Multi-user access across several devices
- Multi-branch restaurant support
- Cloud hosting and remote access
- POS integration
- Payment or deposit handling

These features should be estimated separately after the core application is stable.

## 10. Summary

The existing project is a useful prototype with a graphical interface, MySQL integration and basic reservation/table-management workflows.

The largest gap between the current prototype and a professional application is the reliability of the reservation rules and data handling. In particular, availability, overlapping bookings, table capacity, database consistency, error handling and automated testing need to be addressed.

With one experienced developer working full-time and the scope described above, a realistic estimate for a professional first release is **approximately 8–10 weeks**. The estimate should be revised after confirming the restaurant's exact operating rules and reviewing the application in its target environment.

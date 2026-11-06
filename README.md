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



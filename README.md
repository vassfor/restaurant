# Restaurant Reservation Manager

A desktop restaurant table and reservation manager built with Python, Tkinter, and MySQL.

## Architecture

The application is now split into clear layers:

```text
main.py
  └── application bootstrap
      ├── config.py          configuration
      ├── database.py        MySQL lifecycle
      ├── repositories.py    SQL persistence
      ├── services.py        validation and business rules
      ├── storage.py         local business metadata
      ├── setup_wizard.py           first-run setup UI
      └── app.py             Tkinter presentation and user interaction
```

### Responsibilities

- `main.py` starts the application and wires dependencies together.
- `config.py` contains database configuration and environment-variable support.
- `database.py` owns database initialization and connections.
- `repositories.py` contains SQL queries and persistence operations.
- `services.py` contains validation and business rules without Tkinter code.
- `storage.py` manages `business_data.json`.
- `setup.py` handles first-run configuration.
- `app.py` contains the desktop UI and delegates data operations to services.
- `models.py` defines the `Table` and `Reservation` domain models.

The UI no longer opens MySQL connections, performs SQL queries, or edits JSON directly.

## Requirements

- Python 3.10+
- MySQL Server
- MySQL Connector/Python
- Tkinter

Install the Python dependency:

```bash
pip install mysql-connector-python
```

Tkinter is included with most Python installations. On some Linux distributions it must be installed separately through the operating system package manager.

## Database configuration

Defaults:

```text
Host: localhost
User: root
Password: empty
Database: restaurant
```

You can override them with environment variables:

```text
RESTAURANT_DB_HOST
RESTAURANT_DB_USER
RESTAURANT_DB_PASSWORD
RESTAURANT_DB_NAME
```

Example:

```bash
RESTAURANT_DB_USER=restaurant_user
RESTAURANT_DB_PASSWORD=secret
python main.py
```

The application creates the database and required tables automatically when the configured MySQL account has permission to do so.

## First run

1. Start MySQL.
2. Configure the database credentials if the defaults are not suitable.
3. Run:

```bash
python main.py
```

4. If `business_data.json` does not exist, the setup wizard asks for the restaurant name and table definitions.
5. The database is initialized automatically.
6. On subsequent launches, the application loads the business metadata and tables.

Existing `business_data.json` data is used to populate an empty database once, so the refactor can be introduced without losing the existing table configuration.

## Features

- Create and remove restaurant tables.
- Track manual table occupancy.
- Create reservations.
- Validate customer name, phone, date, time, party size, and table.
- Edit reservations.
- Cancel reservations.
- View reservations by date.
- Automatically display reservations in the current two-hour status window.
- Remove expired reservations.
- Persist restaurant/table configuration locally and reservation data in MySQL.

## Data ownership

MySQL is the source of truth for tables and reservations during normal operation.

`business_data.json` stores lightweight restaurant metadata and a synchronized table snapshot. It is retained for first-run setup and migration compatibility.

Do not edit `business_data.json` while the application is running.

## Project structure

```text
restaurant-main/
├── app.py
├── business_data.json
├── config.py
├── database.py
├── main.py
├── models.py
├── repositories.py
├── services.py
├── setup_wizard.py
├── storage.py
└── README.md
```

## Development

The codebase keeps database access behind repositories, which makes the business logic easier to test independently from Tkinter and MySQL.

A useful next step for further development is adding automated tests for `services.py` with repository fakes.

## Notes

The project uses Greek UI labels while keeping the source code and architecture names in English.

No credentials are stored in source code beyond the original local-development defaults. For production use, provide database credentials through environment variables and use a dedicated MySQL account instead of `root`.

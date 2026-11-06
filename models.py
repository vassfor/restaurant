from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class Table:
    name: str
    capacity: int


@dataclass(frozen=True)
class Reservation:
    id: int
    table_name: str
    name: str
    phone: str
    date: date
    time: time
    people: int

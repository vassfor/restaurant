import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = "localhost"
    user: str = "root"
    password: str = ""
    database: str = "restaurant"

    @classmethod
    def from_env(cls):
        return cls(
            host=os.getenv("RESTAURANT_DB_HOST", "localhost"),
            user=os.getenv("RESTAURANT_DB_USER", "root"),
            password=os.getenv("RESTAURANT_DB_PASSWORD", ""),
            database=os.getenv("RESTAURANT_DB_NAME", "restaurant"),
        )

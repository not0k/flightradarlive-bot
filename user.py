from dataclasses import dataclass


@dataclass(slots=True)
class User:
    id: int
    latitude: float
    longitude: float
    radius: int = 2500
    min_altitude: int = 0
    max_altitude: int = 50000

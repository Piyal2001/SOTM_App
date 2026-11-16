
import math
from datetime import datetime, timezone


class MovingGroundStation:
    """
    Simulates a ground terminal moving at constant speed
    and constant heading over a spherical Earth.
    """

    EARTH_RADIUS_KM = 6371.0088

    def __init__(
        self,
        name,
        start_latitude,
        start_longitude,
        speed_kmh,
        heading_deg,
        start_time,
        altitude_km=0.0
    ):

        # Validate starting coordinates
        if not -90 <= start_latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")

        if not -180 <= start_longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")

        if speed_kmh < 0:
            raise ValueError("Vehicle speed cannot be negative.")

        if not 0 <= heading_deg <= 360:
            raise ValueError("Heading must be between 0 and 360 degrees.")

        if altitude_km < -0.5:
            raise ValueError("Invalid ground terminal altitude.")

        if not isinstance(start_time, datetime):
            raise TypeError("start_time must be a datetime object.")

        if start_time.tzinfo is None or start_time.utcoffset() is None:
            raise ValueError("start_time must include a timezone.")

        self.name = name

        self.start_latitude = float(start_latitude)
        self.start_longitude = float(start_longitude)

        self.speed_kmh = float(speed_kmh)
        self.heading_deg = float(heading_deg) % 360

        self.start_time = start_time.astimezone(timezone.utc)
        self.altitude_km = float(altitude_km)

    def get_position(self, simulation_time):
        """
        Calculate vehicle latitude and longitude at a given time.

        Heading convention:
        0 degrees   = North
        90 degrees  = East
        180 degrees = South
        270 degrees = West
        """

        if not isinstance(simulation_time, datetime):
            raise TypeError("simulation_time must be a datetime object.")

        if simulation_time.tzinfo is None or simulation_time.utcoffset() is None:
            raise ValueError("simulation_time must include a timezone.")

        simulation_time = simulation_time.astimezone(timezone.utc)

        elapsed_seconds = (
            simulation_time - self.start_time
        ).total_seconds()

        if elapsed_seconds < 0:
            raise ValueError(
                "Simulation time cannot be earlier than vehicle start time."
            )

        # Calculate distance travelled in kilometres
        distance_km = (
            self.speed_kmh * elapsed_seconds / 3600
        )

        # Convert coordinates and heading to radians
        lat1 = math.radians(self.start_latitude)
        lon1 = math.radians(self.start_longitude)
        bearing = math.radians(self.heading_deg)

        # Angular distance travelled
        angular_distance = (
            distance_km / self.EARTH_RADIUS_KM
        )

        # Great-circle destination calculation
        lat2 = math.asin(
            math.sin(lat1) * math.cos(angular_distance)
            +
            math.cos(lat1) * math.sin(angular_distance)
            * math.cos(bearing)
        )

        lon2 = lon1 + math.atan2(
            math.sin(bearing) * math.sin(angular_distance)
            * math.cos(lat1),
            math.cos(angular_distance)
            - math.sin(lat1) * math.sin(lat2)
        )

        # Convert back to degrees
        latitude = math.degrees(lat2)

        longitude = (
            math.degrees(lon2) + 180
        ) % 360 - 180

        return {
            "time_utc": simulation_time,
            "latitude_deg": latitude,
            "longitude_deg": longitude,
            "altitude_km": self.altitude_km,
            "distance_travelled_km": distance_km
        }

    def get_station_info(self):
        """Return the initial vehicle configuration."""

        return {
            "name": self.name,
            "start_latitude_deg": self.start_latitude,
            "start_longitude_deg": self.start_longitude,
            "speed_kmh": self.speed_kmh,
            "heading_deg": self.heading_deg,
            "start_time_utc": self.start_time,
            "altitude_km": self.altitude_km
        }

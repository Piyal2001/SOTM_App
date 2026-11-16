
import pandas as pd

from datetime import datetime, timedelta, timezone

from skyfield.api import load, wgs84


class MovingSatelliteGeometry:
    """
    Calculates satellite geometry relative to a moving ground terminal.
    """

    def __init__(self, satellite_orbit):
        self.satellite_orbit = satellite_orbit
        self.satellite = satellite_orbit.satellite

        # Skyfield time scale
        self.ts = load.timescale()

    def calculate_geometry(
        self,
        moving_ground_station,
        simulation_time
    ):
        """
        Calculate satellite azimuth, elevation and range
        relative to the moving vehicle at a given time.
        """

        if not isinstance(simulation_time, datetime):
            raise TypeError("simulation_time must be a datetime object.")

        if simulation_time.tzinfo is None or simulation_time.utcoffset() is None:
            raise ValueError("simulation_time must include a timezone.")

        simulation_time = simulation_time.astimezone(timezone.utc)

        # Get vehicle position at this timestamp
        vehicle_position = moving_ground_station.get_position(
            simulation_time
        )

        latitude = vehicle_position["latitude_deg"]
        longitude = vehicle_position["longitude_deg"]
        altitude_km = vehicle_position["altitude_km"]

        # Convert vehicle coordinates into a Skyfield location
        station_position = wgs84.latlon(
            latitude_degrees=latitude,
            longitude_degrees=longitude,
            elevation_m=altitude_km * 1000
        )

        # Convert Python datetime into Skyfield time
        skyfield_time = self.ts.from_datetime(simulation_time)

        # Calculate satellite position relative to vehicle
        difference = self.satellite - station_position

        topocentric = difference.at(skyfield_time)

        # Calculate azimuth, elevation and slant range
        elevation, azimuth, distance = topocentric.altaz()

        # Convert elevation into the signed range -180 to +180 degrees
        elevation_deg = elevation.degrees
        azimuth_deg = azimuth.degrees % 360
        

        return {
            "time_utc": simulation_time,
            "vehicle_latitude_deg": latitude,
            "vehicle_longitude_deg": longitude,
            "vehicle_altitude_km": altitude_km,
            "distance_travelled_km":
                vehicle_position["distance_travelled_km"],
            "slant_range_km": distance.km,
            "azimuth_deg": azimuth_deg,
            "elevation_deg": elevation_deg,
            "visible": elevation_deg > 0
        }

    def generate_tracking_data(
        self,
        moving_ground_station,
        start_time,
        duration_minutes=90,
        interval_seconds=30
    ):
        """
        Generate satellite tracking data for a moving vehicle.
        """

        if not isinstance(start_time, datetime):
            raise TypeError("start_time must be a datetime object.")

        if start_time.tzinfo is None or start_time.utcoffset() is None:
            raise ValueError("start_time must include a timezone.")

        if duration_minutes <= 0:
            raise ValueError("Duration must be positive.")

        if interval_seconds <= 0:
            raise ValueError("Interval must be positive.")

        start_time = start_time.astimezone(timezone.utc)

        # The vehicle and simulation must start together
        if start_time != moving_ground_station.start_time:
            raise ValueError(
                "Simulation start time must match vehicle start time."
            )

        total_seconds = int(duration_minutes * 60)

        timestamps = range(
            0,
            total_seconds + 1,
            interval_seconds
        )

        tracking_results = []

        for elapsed_seconds in timestamps:

            current_time = start_time + timedelta(
                seconds=elapsed_seconds
            )

            result = self.calculate_geometry(
                moving_ground_station,
                current_time
            )

            tracking_results.append(result)

        return pd.DataFrame(tracking_results)

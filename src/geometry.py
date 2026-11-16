
from datetime import timezone
from skyfield.api import wgs84


class SatelliteGeometry:

    def __init__(self, satellite_orbit, ground_station):

        self.satellite_orbit = satellite_orbit
        self.ground_station = ground_station

        # Convert ground station coordinates into
        # a Skyfield geographic position.

        self.station_position = wgs84.latlon(
            latitude_degrees=ground_station.latitude,
            longitude_degrees=ground_station.longitude,
            elevation_m=ground_station.altitude_km * 1000
        )

    # ======================================
    # 1. CALCULATE SATELLITE GEOMETRY
    # ======================================

    def calculate(self, simulation_time):

        if simulation_time.tzinfo is None:
            raise ValueError(
                "Simulation time must include timezone information."
            )

        simulation_time = simulation_time.astimezone(timezone.utc)

        # Convert simulation time into Skyfield time.

        t = self.satellite_orbit.timescale.from_datetime(
            simulation_time
        )

        # Calculate satellite position relative
        # to the ground station.

        difference = (
            self.satellite_orbit.satellite
            - self.station_position
        )

        topocentric = difference.at(t)

        # Calculate azimuth, elevation and distance.

        elevation, azimuth, distance = topocentric.altaz()

        azimuth_deg = azimuth.degrees
        elevation_deg = elevation.degrees
        slant_range_km = distance.km

        # Check whether satellite is above horizon.

        visible = elevation_deg > 0

        return {
            "time_utc": simulation_time,
            "azimuth_deg": azimuth_deg,
            "elevation_deg": elevation_deg,
            "slant_range_km": slant_range_km,
            "visible": visible
        }

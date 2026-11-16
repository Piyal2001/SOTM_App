
from datetime import timezone


class SatellitePassPredictor:

    def __init__(self, satellite_orbit, ground_station):

        self.satellite = satellite_orbit.satellite
        self.timescale = satellite_orbit.timescale

        from skyfield.api import wgs84

        self.station = wgs84.latlon(
            latitude_degrees=ground_station.latitude,
            longitude_degrees=ground_station.longitude,
            elevation_m=ground_station.altitude_km * 1000
        )

    # ======================================
    # 1. PREDICT SATELLITE PASSES
    # ======================================

    def predict_passes(
        self,
        start_time,
        duration_days=7,
        elevation_mask_deg=10
    ):

        if start_time.tzinfo is None:
            raise ValueError(
                "Start time must include timezone information."
            )

        if not 0 <= elevation_mask_deg <= 90:
            raise ValueError(
                "Elevation mask must be between 0 and 90 degrees."
            )

        start_time = start_time.astimezone(timezone.utc)
        from datetime import timedelta
        end_time = start_time + timedelta(days=duration_days)

        t0 = self.timescale.from_datetime(start_time)
        t1 = self.timescale.from_datetime(end_time)

        times, events = self.satellite.find_events(
            self.station,
            t0,
            t1,
            altitude_degrees=elevation_mask_deg
        )

        passes = []
        current_pass = {}

        for time, event in zip(times, events):

            event_time = time.utc_datetime()

            if event == 0:

                current_pass = {
                    "aos_utc": event_time
                }

            elif event == 1:

                if current_pass:
                    current_pass["maximum_elevation_utc"] = event_time

                    topocentric = (
                     self.satellite - self.station
                     ).at(time)

                    altitude, azimuth, distance = topocentric.altaz()

                    current_pass["maximum_elevation_deg"] = (
                     altitude.degrees
                        )

            elif event == 2:

                if current_pass:

                    current_pass["los_utc"] = event_time

                    duration = (
                        current_pass["los_utc"]
                        - current_pass["aos_utc"]
                    ).total_seconds() / 60

                    current_pass["duration_minutes"] = duration

                    passes.append(current_pass)
                    current_pass = {}

        return passes

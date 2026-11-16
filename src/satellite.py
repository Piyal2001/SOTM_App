
from skyfield.api import EarthSatellite, load
from sgp4.api import Satrec
from datetime import timezone


class SatelliteOrbit:

    def __init__(self, name, tle_line1, tle_line2):

        self.name = name
        self.tle_line1 = tle_line1.strip()
        self.tle_line2 = tle_line2.strip()

        self.validate_tle()

        self.timescale = load.timescale()

        self.satellite = EarthSatellite(
            self.tle_line1,
            self.tle_line2,
            self.name,
            self.timescale
        )

        self.sgp4_satellite = Satrec.twoline2rv(
            self.tle_line1,
            self.tle_line2
        )

    # ======================================
    # 1. TLE VALIDATION
    # ======================================

    def validate_tle(self):

        if not self.tle_line1.startswith("1 "):
            raise ValueError("Invalid TLE Line 1.")

        if not self.tle_line2.startswith("2 "):
            raise ValueError("Invalid TLE Line 2.")

        if len(self.tle_line1) != 69:
            raise ValueError("TLE Line 1 must contain 69 characters.")

        if len(self.tle_line2) != 69:
            raise ValueError("TLE Line 2 must contain 69 characters.")

    # ======================================
    # 2. TLE AGE CHECK
    # ======================================

    def check_tle_age(self, simulation_time):

        if simulation_time.tzinfo is None:
            raise ValueError(
                "Simulation time must include timezone information."
            )

        simulation_time = simulation_time.astimezone(timezone.utc)

        tle_epoch = self.satellite.epoch.utc_datetime()

        age_days = (
            simulation_time - tle_epoch
        ).total_seconds() / 86400

        if age_days < 0:
            status = "Simulation time is before TLE epoch."

        elif age_days > 7:
            status = "WARNING: TLE is older than 7 days."

        else:
            status = "TLE age is within the initial 7-day screening limit."

        return {
            "tle_epoch": tle_epoch,
            "age_days": age_days,
            "status": status
        }

    # ======================================
    # 3. SATELLITE POSITION
    # ======================================

    def get_position(self, simulation_time):

        if simulation_time.tzinfo is None:
            raise ValueError(
                "Simulation time must include timezone information."
            )

        simulation_time = simulation_time.astimezone(timezone.utc)

        t = self.timescale.from_datetime(simulation_time)

        geocentric = self.satellite.at(t)

        print("SGP4 propagation error:", geocentric.message)

        subpoint = geocentric.subpoint()

        latitude = subpoint.latitude.degrees
        longitude = subpoint.longitude.degrees
        altitude_km = subpoint.elevation.km

        return {
            "time_utc": simulation_time,
            "latitude_deg": latitude,
            "longitude_deg": longitude,
            "altitude_km": altitude_km
        }

    # ======================================
    # 4. ECI POSITION AND VELOCITY
    # ======================================

    def get_position_eci(self, simulation_time):

        if simulation_time.tzinfo is None:
            raise ValueError(
                "Simulation time must include timezone information."
            )

        simulation_time = simulation_time.astimezone(timezone.utc)

        t = self.timescale.from_datetime(simulation_time)

        geocentric = self.satellite.at(t)

        position_km = geocentric.position.km
        velocity_km_s = geocentric.velocity.km_per_s

        return {
            "x_km": position_km[0],
            "y_km": position_km[1],
            "z_km": position_km[2],
            "vx_km_s": velocity_km_s[0],
            "vy_km_s": velocity_km_s[1],
            "vz_km_s": velocity_km_s[2]
        }

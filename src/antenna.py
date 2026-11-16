
import math


class AntennaPointing:

    def __init__(
        self,
        beamwidth_deg=2.0,
        azimuth_offset_deg=0.5,
        elevation_offset_deg=0.5
    ):

        self.beamwidth_deg = float(beamwidth_deg)
        self.azimuth_offset_deg = float(azimuth_offset_deg)
        self.elevation_offset_deg = float(elevation_offset_deg)

        self.validate_parameters()

    # ======================================
    # 1. VALIDATE ANTENNA PARAMETERS
    # ======================================

    def validate_parameters(self):

        if self.beamwidth_deg <= 0:
            raise ValueError(
                "Antenna beamwidth must be greater than zero."
            )

        if self.beamwidth_deg > 180:
            raise ValueError(
                "Antenna beamwidth cannot exceed 180 degrees."
            )

        if not -90 <= self.elevation_offset_deg <= 90:
            raise ValueError(
                "Invalid elevation offset."
            )

    # ======================================
    # 2. CALCULATE POINTING ERROR
    # ======================================

    def calculate_pointing_error(
        self,
        desired_azimuth,
        desired_elevation
    ):

        actual_azimuth = (
            desired_azimuth + self.azimuth_offset_deg
        ) % 360

        actual_elevation = (
            desired_elevation + self.elevation_offset_deg
        )

        if not -90 <= actual_elevation <= 90:
            raise ValueError(
                "Actual antenna elevation is outside valid limits."
            )

        # Convert angles into radians

        az1 = math.radians(desired_azimuth)
        el1 = math.radians(desired_elevation)

        az2 = math.radians(actual_azimuth)
        el2 = math.radians(actual_elevation)

        # Angular separation between two directions

        cosine_angle = (
            math.sin(el1) * math.sin(el2)
            +
            math.cos(el1) * math.cos(el2)
            * math.cos(az1 - az2)
        )

        cosine_angle = max(
            -1.0,
            min(1.0, cosine_angle)
        )

        pointing_error = math.degrees(
            math.acos(cosine_angle)
        )

        return {
            "desired_azimuth_deg": desired_azimuth,
            "actual_azimuth_deg": actual_azimuth,
            "desired_elevation_deg": desired_elevation,
            "actual_elevation_deg": actual_elevation,
            "pointing_error_deg": pointing_error
        }

    # ======================================
    # 3. CALCULATE ANTENNA POINTING LOSS
    # ======================================

    def calculate_pointing_loss(self, pointing_error_deg):

        pointing_loss_db = (
            12.0
            * (pointing_error_deg / self.beamwidth_deg) ** 2
        )

        return pointing_loss_db

    # ======================================
    # 4. COMPLETE ANTENNA ANALYSIS
    # ======================================

    def analyze(self, desired_azimuth, desired_elevation):

        result = self.calculate_pointing_error(
            desired_azimuth,
            desired_elevation
        )

        pointing_loss = self.calculate_pointing_loss(
            result["pointing_error_deg"]
        )

        result["beamwidth_deg"] = self.beamwidth_deg
        result["pointing_loss_db"] = pointing_loss

        return result

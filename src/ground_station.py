
class GroundStation:

    def __init__(
        self,
        name,
        latitude,
        longitude,
        altitude_km=0.0
    ):

        self.name = name
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.altitude_km = float(altitude_km)

        self.validate_coordinates()

    # ======================================
    # 1. COORDINATE VALIDATION
    # ======================================

    def validate_coordinates(self):

        if not -90 <= self.latitude <= 90:
            raise ValueError(
                "Latitude must be between -90 and 90 degrees."
            )

        if not -180 <= self.longitude <= 180:
            raise ValueError(
                "Longitude must be between -180 and 180 degrees."
            )

        if self.altitude_km < -0.5:
            raise ValueError(
                "Ground station altitude is below the allowed limit."
            )

    # ======================================
    # 2. GET STATION INFORMATION
    # ======================================

    def get_station_info(self):

        return {
            "name": self.name,
            "latitude_deg": self.latitude,
            "longitude_deg": self.longitude,
            "altitude_km": self.altitude_km
        }

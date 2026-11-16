
from src.antenna_tracking import AntennaTracker
from src.link_tracking import LinkTracker


class MovingTerminalTracker:
    """
    Integrates moving-terminal geometry, antenna pointing,
    and link-budget calculations.
    """

    def __init__(
        self,
        antenna,
        link_budget,
        elevation_mask_deg=10.0
    ):

        if not 0 <= elevation_mask_deg <= 90:
            raise ValueError(
                "Elevation mask must be between 0 and 90 degrees."
            )

        self.antenna = antenna
        self.link_budget = link_budget
        self.elevation_mask_deg = elevation_mask_deg

        self.antenna_tracker = AntennaTracker(antenna)
        self.link_tracker = LinkTracker(link_budget)

    def process_tracking_data(self, tracking_data):
        """
        Process moving-terminal geometry through the antenna
        and link-budget models.

        Returns antenna results and combined link results.
        """

        required_columns = [
            "time_utc",
            "azimuth_deg",
            "elevation_deg",
            "slant_range_km"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in tracking_data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing tracking columns: {missing_columns}"
            )

        if tracking_data.empty:
            raise ValueError("Tracking data cannot be empty.")

        # Stage 1: Antenna pointing calculations
        antenna_results = (
            self.antenna_tracker.process_tracking_data(
                tracking_data
            )
        )

        # Stage 2: Link-budget calculations
        link_results = self.link_tracker.process_link_data(
            tracking_data,
            antenna_results,
            elevation_mask_deg=self.elevation_mask_deg
        )

        return {
            "antenna_results": antenna_results,
            "link_results": link_results
        }

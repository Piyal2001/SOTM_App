
import pandas as pd

from src.antenna import AntennaPointing


class AntennaTracker:

    def __init__(self, antenna):

        self.antenna = antenna

    def process_tracking_data(self, tracking_data):

        results = []

        for _, row in tracking_data.iterrows():

            analysis = self.antenna.analyze(
                desired_azimuth=row["azimuth_deg"],
                desired_elevation=row["elevation_deg"]
            )

            results.append(analysis)

        antenna_data = pd.DataFrame(results)

        final_data = pd.concat(
            [
                tracking_data.reset_index(drop=True),
                antenna_data.reset_index(drop=True)
            ],
            axis=1
        )

        return final_data

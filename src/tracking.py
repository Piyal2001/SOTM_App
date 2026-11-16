
import pandas as pd
from datetime import timedelta


class SatelliteTracker:

    def __init__(self, geometry_engine):

        self.geometry_engine = geometry_engine

    # ======================================
    # 1. GENERATE TIME-SERIES DATA
    # ======================================

    def generate_tracking_data(
        self,
        start_time,
        duration_minutes=90,
        interval_seconds=30
    ):

        if start_time.tzinfo is None:
            raise ValueError(
                "Start time must include timezone information."
            )

        if duration_minutes <= 0:
            raise ValueError(
                "Duration must be greater than zero."
            )

        if interval_seconds <= 0:
            raise ValueError(
                "Interval must be greater than zero."
            )

        records = []

        total_steps = int(
            duration_minutes * 60 / interval_seconds
        )

        for step in range(total_steps + 1):

            current_time = start_time + timedelta(
                seconds=step * interval_seconds
            )

            result = self.geometry_engine.calculate(
                current_time
            )

            records.append(result)

        dataframe = pd.DataFrame(records)

        return dataframe

    # ======================================
    # 2. GENERATE VISIBILITY INFORMATION
    # ======================================

   
def get_visibility_summary(self, dataframe):

    maximum_elevation = dataframe[
        "elevation_deg"
    ].max()

    maximum_elevation_time = dataframe.loc[
        dataframe["elevation_deg"].idxmax(),
        "time_utc"
    ]

    visible_data = dataframe[
        dataframe["visible"] == True
    ]

    if visible_data.empty:

        return {
            "visibility": "NO PASS",
            "aos": None,
            "los": None,
            "maximum_elevation_deg": maximum_elevation,
            "maximum_elevation_time": maximum_elevation_time,
            "visibility_duration_minutes": 0
        }

    aos = visible_data.iloc[0]["time_utc"]
    los = visible_data.iloc[-1]["time_utc"]

    duration = (
        (los - aos).total_seconds() / 60
    )

    return {
        "visibility": "PASS DETECTED",
        "aos": aos,
        "los": los,
        "maximum_elevation_deg": maximum_elevation,
        "maximum_elevation_time": maximum_elevation_time,
        "visibility_duration_minutes": duration
    }

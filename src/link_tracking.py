
import pandas as pd
from src.link_budget import LinkBudget


class LinkTracker:

    def __init__(self, link_budget):

        self.link_budget = link_budget

    # ======================================
    # 1. PROCESS TRACKING AND ANTENNA DATA
    # ======================================

    def process_link_data(
        self,
        tracking_data,
        antenna_data,
        elevation_mask_deg=10.0
    ):

        if len(tracking_data) != len(antenna_data):
            raise ValueError(
                "Tracking and antenna datasets must have equal lengths."
            )

        tracking_data = tracking_data.reset_index(drop=True).copy()
        antenna_data = antenna_data.reset_index(drop=True).copy()

        if not tracking_data["time_utc"].equals(
            antenna_data["time_utc"]
        ):
            raise ValueError(
                "Tracking and antenna timestamps do not match."
            )

        if elevation_mask_deg < 0 or elevation_mask_deg > 90:
            raise ValueError(
                "Elevation mask must be between 0 and 90 degrees."
            )

        results = []

        # ==================================
        # 2. CALCULATE LINK PARAMETERS
        # ==================================

        for index, row in tracking_data.iterrows():

            distance_km = row["slant_range_km"]

            pointing_loss = antenna_data.loc[
                index, "pointing_loss_db"
            ]

            elevation = row["elevation_deg"]

            fspl = self.link_budget.calculate_fspl(
                distance_km
            )

            # A link is operational only when
            # the satellite meets the elevation mask.

            link_available = elevation >= elevation_mask_deg

            if link_available:

                result = self.link_budget.analyze(
                    distance_km=distance_km,
                    pointing_loss_db=pointing_loss
                )

                received_power = result[
                    "received_power_dbm"
                ]

                noise_power = result[
                    "noise_power_dbm"
                ]

                snr = result["snr_db"]

            else:

                received_power = None
                noise_power = None
                snr = None

            results.append({

                "fspl_db": fspl,

                "received_power_dbm": received_power,

                "noise_power_dbm": noise_power,

                "pointing_loss_db": pointing_loss,

                "snr_db": snr,

                "link_available": link_available

            })

        link_results = pd.DataFrame(results)

        final_data = pd.concat(
            [
                tracking_data,
                antenna_data[
                    [
                        "pointing_error_deg"
                    ]
                ],
                link_results
            ],
            axis=1
        )

        return final_data

    # ======================================
    # 3. LINK PERFORMANCE SUMMARY
    # ======================================

    def get_link_summary(self, dataframe):

        available = dataframe[
            dataframe["link_available"] == True
        ]

        if available.empty:

            return {
                "status": "NO OPERATIONAL LINK",
                "available_samples": 0,
                "link_availability_percent": 0.0,
                "mean_snr_db": None,
                "minimum_snr_db": None,
                "maximum_snr_db": None,
                "mean_received_power_dbm": None
            }

        availability = (
            len(available) / len(dataframe)
        ) * 100

        return {

            "status": "LINK DETECTED",

            "available_samples": len(available),

            "link_availability_percent": availability,

            "mean_snr_db": available["snr_db"].mean(),

            "minimum_snr_db": available["snr_db"].min(),

            "maximum_snr_db": available["snr_db"].max(),

            "mean_received_power_dbm": (
                available["received_power_dbm"].mean()
            )
        }


import pandas as pd


class ReliabilityAnalyzer:

    def analyze(
        self,
        dataframe,
        snr_threshold_db=10.0
    ):
        data = dataframe.copy()

        required_columns = [
            "link_available",
            "snr_db"
        ]

        for column in required_columns:
            if column not in data.columns:
                raise ValueError(
                    f"Missing required column: {column}"
                )

        # Geometric availability based on elevation mask
        data["geometric_available"] = (
            data["link_available"].fillna(False).astype(bool)
        )

        # SNR-qualified communication availability
        data["snr_qualified"] = (
            data["geometric_available"]
            & data["snr_db"].notna()
            & (data["snr_db"] >= snr_threshold_db)
        )

        total_samples = len(data)

        if total_samples == 0:
            raise ValueError("Input dataframe is empty.")

        geometric_samples = int(
            data["geometric_available"].sum()
        )

        reliable_samples = int(
            data["snr_qualified"].sum()
        )

        # Availability over the complete simulation window
        overall_availability = (
            reliable_samples / total_samples
        ) * 100

        outage_probability = (
            1 - reliable_samples / total_samples
        ) * 100

        # SNR outage among geometrically available samples
        if geometric_samples > 0:
            snr_outage_probability = (
                (geometric_samples - reliable_samples)
                / geometric_samples
            ) * 100
        else:
            snr_outage_probability = None

        summary = {
            "total_samples": total_samples,
            "geometric_available_samples": geometric_samples,
            "reliable_samples": reliable_samples,
            "snr_threshold_db": snr_threshold_db,
            "overall_availability_percent": overall_availability,
            "overall_outage_probability_percent": outage_probability,
            "snr_outage_probability_percent": snr_outage_probability
        }

        return data, summary

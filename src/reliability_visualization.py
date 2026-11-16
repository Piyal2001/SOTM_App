
import plotly.express as px


class ReliabilityVisualizer:

    def __init__(self, dataframe):
        self.dataframe = dataframe.copy()

    def plot_availability(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="snr_qualified",
            title="Communication Reliability vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "snr_qualified": "Reliable Link"
            }
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    def plot_snr_outage(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="snr_db",
            title="SNR During Satellite Pass",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "snr_db": "SNR (dB)"
            }
        )

        fig.add_hline(
            y=10,
            line_dash="dash",
            annotation_text="10 dB SNR Threshold"
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    def save_graphs(
        self,
        output_folder="results/graphs/reliability"
    ):

        import os

        os.makedirs(output_folder, exist_ok=True)

        self.plot_availability().write_html(
            f"{output_folder}/communication_reliability.html"
        )

        self.plot_snr_outage().write_html(
            f"{output_folder}/snr_reliability.html"
        )

        print("Reliability graphs saved successfully.")

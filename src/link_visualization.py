
import plotly.express as px


class LinkVisualizer:

    def __init__(self, dataframe):

        self.dataframe = dataframe.copy()

    # ======================================
    # 1. RECEIVED POWER GRAPH
    # ======================================

    def plot_received_power(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="received_power_dbm",
            title="Received Signal Power vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "received_power_dbm": "Received Power (dBm)"
            }
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    # ======================================
    # 2. SNR GRAPH
    # ======================================

    def plot_snr(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="snr_db",
            title="Signal-to-Noise Ratio vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "snr_db": "SNR (dB)"
            }
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    # ======================================
    # 3. FSPL GRAPH
    # ======================================

    def plot_fspl(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="fspl_db",
            title="Free Space Path Loss vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "fspl_db": "FSPL (dB)"
            }
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    # ======================================
    # 4. SAVE GRAPHS
    # ======================================

    def save_graphs(self, output_folder="results/graphs"):

        import os

        os.makedirs(output_folder, exist_ok=True)

        self.plot_received_power().write_html(
            f"{output_folder}/received_power_vs_time.html"
        )

        self.plot_snr().write_html(
            f"{output_folder}/snr_vs_time.html"
        )

        self.plot_fspl().write_html(
            f"{output_folder}/fspl_vs_time.html"
        )

        print("Link budget graphs saved successfully.")

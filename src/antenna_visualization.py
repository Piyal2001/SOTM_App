
import plotly.express as px


class AntennaVisualizer:

    def __init__(self, dataframe):
        self.dataframe = dataframe.copy()

    # ======================================
    # 1. POINTING ERROR GRAPH
    # ======================================

    def plot_pointing_error(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="pointing_error_deg",
            title="Antenna Pointing Error vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "pointing_error_deg": "Pointing Error (Degrees)"
            }
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    # ======================================
    # 2. POINTING LOSS GRAPH
    # ======================================

    def plot_pointing_loss(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="pointing_loss_db",
            title="Antenna Pointing Loss vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "pointing_loss_db": "Pointing Loss (dB)"
            }
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    # ======================================
    # 3. SAVE GRAPHS
    # ======================================

    def save_graphs(self, output_folder="results/graphs"):

        import os

        os.makedirs(output_folder, exist_ok=True)

        self.plot_pointing_error().write_html(
            os.path.join(
                output_folder,
                "pointing_error_vs_time.html"
            )
        )

        self.plot_pointing_loss().write_html(
            os.path.join(
                output_folder,
                "pointing_loss_vs_time.html"
            )
        )

        print("Antenna graphs saved successfully.")


import plotly.express as px


class SatelliteVisualizer:

    def __init__(self, dataframe):

        self.dataframe = dataframe.copy()

    # ======================================
    # 1. AZIMUTH VS TIME
    # ======================================

    def plot_azimuth(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="azimuth_deg",
            title="Satellite Azimuth vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "azimuth_deg": "Azimuth (Degrees)"
            }
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    # ======================================
    # 2. ELEVATION VS TIME
    # ======================================

    def plot_elevation(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="elevation_deg",
            title="Satellite Elevation vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "elevation_deg": "Elevation (Degrees)"
            }
        )

        # Horizon reference line
        fig.add_hline(
            y=0,
            line_dash="dash",
            annotation_text="Geometric Horizon"
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    # ======================================
    # 3. SLANT RANGE VS TIME
    # ======================================

    def plot_slant_range(self):

        fig = px.line(
            self.dataframe,
            x="time_utc",
            y="slant_range_km",
            title="Satellite Slant Range vs Time",
            labels={
                "time_utc": "Simulation Time (UTC)",
                "slant_range_km": "Slant Range (km)"
            }
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified"
        )

        return fig

    # ======================================
    # 4. SAVE ALL GRAPHS
    # ======================================

    def save_graphs(self, output_folder="results/graphs"):

        import os

        os.makedirs(output_folder, exist_ok=True)

        self.plot_azimuth().write_html(
            os.path.join(output_folder, "azimuth_vs_time.html")
        )

        self.plot_elevation().write_html(
            os.path.join(output_folder, "elevation_vs_time.html")
        )

        self.plot_slant_range().write_html(
            os.path.join(output_folder, "slant_range_vs_time.html")
        )

        print("All interactive graphs saved successfully.")

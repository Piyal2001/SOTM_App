
import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

# ==========================================
# IMPORT PROJECT MODULES
# ==========================================

from src.satellite import SatelliteOrbit
from src.ground_station import GroundStation
from src.geometry import SatelliteGeometry
from src.tracking import SatelliteTracker
from src.visualization import SatelliteVisualizer
from src.pass_prediction import SatellitePassPredictor

from src.antenna import AntennaPointing
from src.antenna_tracking import AntennaTracker
from src.antenna_visualization import AntennaVisualizer

from src.link_budget import LinkBudget
from src.link_tracking import LinkTracker
from src.link_visualization import LinkVisualizer

from src.reliability import ReliabilityAnalyzer
from src.reliability_visualization import ReliabilityVisualizer


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="SOTM Simulator",
    page_icon="🛰️",
    layout="wide"
)


# ==========================================
# 2. APPLICATION HEADER
# ==========================================

st.title("🛰️ SOTM Simulator")

st.subheader(
    "Satellite Communication On-The-Move "
    "Simulation Platform"
)

st.markdown(
    "An interactive Python-based platform for "
    "satellite tracking, antenna pointing, "
    "link-budget and reliability analysis."
)

st.divider()


# ==========================================
# 3. SIDEBAR CONFIGURATION
# ==========================================

st.sidebar.title("Simulation Configuration")

satellite_mode = "TLE Data"
terminal_mode = "Fixed Ground Station"

st.sidebar.divider()

duration_minutes = st.sidebar.number_input(
    "Simulation Duration (minutes)",
    min_value=1,
    max_value=360,
    value=90
)

interval_seconds = st.sidebar.selectbox(
    "Simulation Time Step (seconds)",
    [1, 5, 10, 30, 60],
    index=3
)

elevation_mask = st.sidebar.number_input(
    "Minimum Elevation (degrees)",
    min_value=0.0,
    max_value=90.0,
    value=10.0
)


# ==========================================
# 4. ANTENNA CONFIGURATION
# ==========================================

st.sidebar.divider()
st.sidebar.subheader("Antenna Configuration")

beamwidth = st.sidebar.number_input(
    "Antenna Beamwidth (degrees)",
    min_value=0.1,
    max_value=180.0,
    value=2.0
)

azimuth_offset = st.sidebar.number_input(
    "Azimuth Offset (degrees)",
    value=0.5
)

elevation_offset = st.sidebar.number_input(
    "Elevation Offset (degrees)",
    value=0.5
)


# ==========================================
# 5. LINK BUDGET CONFIGURATION
# ==========================================

st.sidebar.divider()
st.sidebar.subheader("Link Budget Configuration")

frequency = st.sidebar.number_input(
    "Frequency (GHz)",
    min_value=0.1,
    value=12.0
)

transmit_power = st.sidebar.number_input(
    "Transmit Power (dBm)",
    value=40.0
)

transmit_gain = st.sidebar.number_input(
    "Transmit Antenna Gain (dBi)",
    value=30.0
)

receive_gain = st.sidebar.number_input(
    "Receive Antenna Gain (dBi)",
    value=35.0
)

bandwidth = st.sidebar.number_input(
    "Bandwidth (MHz)",
    min_value=0.1,
    value=10.0
)

noise_figure = st.sidebar.number_input(
    "Noise Figure (dB)",
    value=2.0
)

other_losses = st.sidebar.number_input(
    "Other Losses (dB)",
    value=2.0
)

snr_threshold = st.sidebar.number_input(
    "Minimum SNR Threshold (dB)",
    value=10.0
)


# ==========================================
# 6. SATELLITE CONFIGURATION
# ==========================================

st.header("1. Satellite Configuration")

satellite_name = ""
tle_line1 = ""
tle_line2 = ""

if satellite_mode == "TLE Data":

    satellite_name = st.text_input(
        "Satellite Name",
        value="ISS (ZARYA)"
    )

    tle_line1 = st.text_input(
        "TLE Line 1",
        placeholder="Paste complete TLE Line 1"
    )

    tle_line2 = st.text_input(
        "TLE Line 2",
        placeholder="Paste complete TLE Line 2"
    )

    st.caption(
        "Required CSV columns: timestamp, latitude_deg, "
        "longitude_deg, altitude_km"
    )

    coordinate_file = st.file_uploader(
        "Upload Satellite Coordinate CSV",
        type=["csv"]
    )


# ==========================================
# 7. GROUND TERMINAL CONFIGURATION
# ==========================================

st.divider()

st.header("2. Ground Terminal Configuration")

col1, col2 = st.columns(2)

with col1:

    ground_latitude = st.number_input(
        "Ground Station Latitude (degrees)",
        min_value=-90.0,
        max_value=90.0,
        value=22.5726
    )

    ground_longitude = st.number_input(
        "Ground Station Longitude (degrees)",
        min_value=-180.0,
        max_value=180.0,
        value=88.3639
    )

    ground_altitude = st.number_input(
        "Ground Station Altitude (meters)",
        min_value=-500.0,
        max_value=10000.0,
        value=10.0
    )

with col2:

    station_name = st.text_input(
        "Ground Station Name",
        value="Kolkata Ground Station"
    )

st.success("Fixed ground station selected.")

# ==========================================
# 8. SIMULATION CONFIGURATION SUMMARY
# ==========================================

st.divider()

st.header("3. Simulation Configuration Summary")

st.subheader("Simulation Date and Time")

col1, col2 = st.columns(2)

with col1:

    selected_date = st.date_input(
        "Simulation Date (UTC)",
        value=datetime.now(timezone.utc).date()
    )

with col2:

    selected_time = st.time_input(
        "Simulation Start Time (UTC)",
        value=datetime.now(timezone.utc).time().replace(
            microsecond=0
        )
    )

simulation_start = datetime.combine(
    selected_date,
    selected_time
).replace(tzinfo=timezone.utc)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Simulation Duration",
    f"{duration_minutes} min"
)

col2.metric(
    "Time Interval",
    f"{interval_seconds} sec"
)

col3.metric(
    "Elevation Mask",
    f"{elevation_mask}°"
)


# ==========================================
# 9. RUN SIMULATION
# ==========================================

st.divider()

st.header("4. Run Complete Simulation")

if st.button(
    "🚀 Run Simulation",
    type="primary",
    width="stretch"
):

    # Clear previous results
    st.session_state.pop(
        "simulation_results",
        None
    )

    # Validate configuration

    if satellite_mode != "TLE Data":

        st.error(
            "Please select TLE Data. "
            "Custom coordinate processing is planned for later."
        )

    elif terminal_mode != "Fixed Ground Station":

        st.error(
            "Please select Fixed Ground Station. "
            "Moving vehicle processing is planned for later."
        )

    elif not satellite_name.strip():

        st.error("Please enter a satellite name.")

    elif not tle_line1.strip() or not tle_line2.strip():

        st.error("Please enter both TLE lines.")

    else:

        try:

            with st.spinner(
                "Running complete satellite communication simulation..."
            ):

                # ----------------------------------
                # A. CREATE SATELLITE
                # ----------------------------------

                satellite = SatelliteOrbit(
                    satellite_name,
                    tle_line1,
                    tle_line2
                )

                tle_info = satellite.check_tle_age(
                    simulation_start
                )

                # ----------------------------------
                # B. CREATE GROUND STATION
                # ----------------------------------

                station = GroundStation(
                    name=station_name,
                    latitude=ground_latitude,
                    longitude=ground_longitude,
                    altitude_km=ground_altitude / 1000
                )

                # ----------------------------------
                # C. SATELLITE PASS PREDICTION
                # ----------------------------------

                pass_predictor = SatellitePassPredictor(
                    satellite,
                    station
                )

                pass_prediction_results = (
                    pass_predictor.predict_passes(
                        start_time=simulation_start,
                        duration_days=7,
                        elevation_mask_deg=elevation_mask
                    )
                )

                # ----------------------------------
                # D. CREATE GEOMETRY ENGINE
                # ----------------------------------

                geometry = SatelliteGeometry(
                    satellite,
                    station
                )

                # ----------------------------------
                # E. GENERATE TRACKING DATA
                # ----------------------------------

                tracker = SatelliteTracker(geometry)

                tracking_data = tracker.generate_tracking_data(
                    start_time=simulation_start,
                    duration_minutes=duration_minutes,
                    interval_seconds=interval_seconds
                )

                tracking_data["visible"] = (
                    tracking_data["elevation_deg"]
                    >= elevation_mask
                )

                # ----------------------------------
                # F. ANTENNA POINTING ANALYSIS
                # ----------------------------------

                antenna = AntennaPointing(
                    beamwidth_deg=beamwidth,
                    azimuth_offset_deg=azimuth_offset,
                    elevation_offset_deg=elevation_offset
                )

                antenna_tracker = AntennaTracker(antenna)

                antenna_results = (
                    antenna_tracker.process_tracking_data(
                        tracking_data
                    )
                )

                # ----------------------------------
                # G. LINK BUDGET ANALYSIS
                # ----------------------------------

                link_budget = LinkBudget(
                    frequency_ghz=frequency,
                    transmit_power_dbm=transmit_power,
                    transmit_gain_dbi=transmit_gain,
                    receive_gain_dbi=receive_gain,
                    bandwidth_mhz=bandwidth,
                    noise_figure_db=noise_figure,
                    other_losses_db=other_losses
                )

                link_tracker = LinkTracker(link_budget)

                link_results = link_tracker.process_link_data(
                    tracking_data,
                    antenna_results,
                    elevation_mask_deg=elevation_mask
                )

                # ----------------------------------
                # H. RELIABILITY ANALYSIS
                # ----------------------------------

                reliability_analyzer = ReliabilityAnalyzer()

                (
                    reliability_results,
                    reliability_summary
                ) = reliability_analyzer.analyze(
                    link_results,
                    snr_threshold_db=snr_threshold
                )

                # ----------------------------------
                # I. SAVE CSV RESULTS
                # ----------------------------------

                os.makedirs(
                    "results/csv",
                    exist_ok=True
                )

                os.makedirs(
                    "results/graphs",
                    exist_ok=True
                )

                tracking_data.to_csv(
                    "results/csv/web_tracking_results.csv",
                    index=False
                )

                antenna_results.to_csv(
                    "results/csv/web_antenna_results.csv",
                    index=False
                )

                link_results.to_csv(
                    "results/csv/web_link_results.csv",
                    index=False
                )

                reliability_results.to_csv(
                    "results/csv/web_reliability_results.csv",
                    index=False
                )

                # ----------------------------------
                # J. SAVE TRACKING GRAPHS
                # ----------------------------------

                satellite_visualizer = SatelliteVisualizer(
                    tracking_data
                )

                satellite_visualizer.save_graphs(
                    "results/graphs"
                )

                # ----------------------------------
                # K. STORE ALL RESULTS TOGETHER
                # ----------------------------------

                simulation_results = {

                    "tracking_data": tracking_data,

                    "antenna_results": antenna_results,

                    "link_results": link_results,

                    "reliability_results": reliability_results,

                    "reliability_summary": reliability_summary,

                    "tle_info": tle_info,

                    "simulation_start": simulation_start,

                    "simulation_duration": duration_minutes,

                    "interval_seconds": interval_seconds,

                    "elevation_mask": elevation_mask,

                    "satellite_name": satellite_name,

                    "pass_prediction_results": (
                        pass_prediction_results
                    )
                }

                # Store only after all calculations succeed
                st.session_state["simulation_results"] = (
                    simulation_results
                )

            st.success(
                "Complete satellite communication simulation "
                "completed successfully!"
            )

        except Exception as error:

            st.error(
                f"Simulation failed: {type(error).__name__}: {error}"
            )

            st.exception(error)


# ==========================================
# 10. DISPLAY SIMULATION RESULTS
# ==========================================

results = st.session_state.get(
    "simulation_results"
)

if results is not None:

    data = results["tracking_data"]

    antenna_data = results["antenna_results"]

    link_data = results["link_results"]

    reliability_data = results["reliability_results"]

    reliability_summary = results["reliability_summary"]

    tle_info = results["tle_info"]

    simulation_start_display = results["simulation_start"]

    simulation_duration_display = results["simulation_duration"]

    interval = results["interval_seconds"]

    satellite_display_name = results["satellite_name"]

    pass_data = results["pass_prediction_results"]

    # ======================================
    # A. SIMULATION DETAILS
    # ======================================

    st.divider()

    st.header("5. Complete Simulation Results")

    st.subheader("Simulation Details")

    st.write(
        "**Simulation Start Time (UTC):**",
        simulation_start_display.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    )

    simulation_end_display = (
        simulation_start_display
        + pd.Timedelta(
            minutes=simulation_duration_display
        )
    )

    st.write(
        "**Simulation End Time (UTC):**",
        simulation_end_display.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    )

    # ======================================
    # B. SATELLITE PASS PREDICTION
    # ======================================

    st.divider()

    st.header("6. Satellite Pass Prediction")

    if pass_data:

        pass_df = pd.DataFrame(pass_data)

        pass_df["aos_utc"] = pd.to_datetime(
            pass_df["aos_utc"],
            utc=True
        )

        pass_df["maximum_elevation_utc"] = pd.to_datetime(
            pass_df["maximum_elevation_utc"],
            utc=True
        )

        pass_df["los_utc"] = pd.to_datetime(
            pass_df["los_utc"],
            utc=True
        )

        st.success(
            f"{len(pass_df)} complete satellite passes "
            "predicted over the next 7 days."
        )

        st.subheader("Predicted Passes")

        st.dataframe(
            pass_df,
            width="stretch",
            hide_index=True
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Passes",
            len(pass_df)
        )

        col2.metric(
            "Highest Elevation",
            f"{pass_df['maximum_elevation_deg'].max():.2f}°"
        )

        col3.metric(
            "Longest Pass",
            f"{pass_df['duration_minutes'].max():.2f} min"
        )

    else:

        st.warning(
            "No complete satellite passes found "
            "within the selected prediction period."
        )

    # ======================================
    # C. SATELLITE INFORMATION
    # ======================================

    st.divider()

    st.subheader("Satellite Information")

    st.write(
        "**Satellite:**",
        satellite_display_name
    )

    st.write(
        "**TLE Epoch:**",
        tle_info["tle_epoch"]
    )

    st.write(
        "**TLE Age:**",
        round(tle_info["age_days"], 3),
        "days"
    )

    st.write(
        "**TLE Status:**",
        tle_info["status"]
    )

    # ======================================
    # D. SATELLITE TRACKING PERFORMANCE
    # ======================================

    st.divider()

    st.header("7. Satellite Tracking Performance")

    if not data.empty:

        visible_data = data[
            data["visible"] == True
        ]

        maximum_elevation = data[
            "elevation_deg"
        ].max()

        maximum_elevation_time = data.loc[
            data["elevation_deg"].idxmax(),
            "time_utc"
        ]

        visible_samples = len(visible_data)

        sampled_visibility_minutes = (
            visible_samples * interval / 60
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Data Points",
            len(data)
        )

        col2.metric(
            "Maximum Elevation",
            f"{maximum_elevation:.2f}°"
        )

        col3.metric(
            "Visible Samples",
            visible_samples
        )

        col4.metric(
            "Sampled Visibility",
            f"{sampled_visibility_minutes:.2f} min"
        )

        st.write(
            "**Maximum elevation time:**",
            maximum_elevation_time
        )

        if visible_samples > 0:

            st.success(
                "Satellite visibility detected at "
                "the selected elevation mask."
            )

            st.write(
                "**First visible sample:**",
                visible_data.iloc[0]["time_utc"]
            )

            st.write(
                "**Last visible sample:**",
                visible_data.iloc[-1]["time_utc"]
            )

        else:

            st.warning(
                "No satellite visibility detected "
                "during this simulation."
            )

        satellite_visualizer = SatelliteVisualizer(data)

        st.subheader("Azimuth vs Time")

        st.plotly_chart(
            satellite_visualizer.plot_azimuth(),
            width="stretch"
        )

        st.subheader("Elevation vs Time")

        st.plotly_chart(
            satellite_visualizer.plot_elevation(),
            width="stretch"
        )

        st.subheader("Slant Range vs Time")

        st.plotly_chart(
            satellite_visualizer.plot_slant_range(),
            width="stretch"
        )

    else:

        st.warning("No satellite tracking data available.")

    # ======================================
    # E. ANTENNA POINTING PERFORMANCE
    # ======================================

    st.divider()

    st.header("8. Antenna Pointing Performance")

    antenna_visible = antenna_data[
        antenna_data["elevation_deg"] >=
        results["elevation_mask"]
    ]

    if len(antenna_visible) > 0:

        mean_pointing_error = (
            antenna_visible["pointing_error_deg"].mean()
        )

        maximum_pointing_error = (
            antenna_visible["pointing_error_deg"].max()
        )

        mean_pointing_loss = (
            antenna_visible["pointing_loss_db"].mean()
        )

        maximum_pointing_loss = (
            antenna_visible["pointing_loss_db"].max()
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Mean Pointing Error",
            f"{mean_pointing_error:.4f}°"
        )

        col2.metric(
            "Maximum Pointing Error",
            f"{maximum_pointing_error:.4f}°"
        )

        col3.metric(
            "Mean Pointing Loss",
            f"{mean_pointing_loss:.4f} dB"
        )

        col4.metric(
            "Maximum Pointing Loss",
            f"{maximum_pointing_loss:.4f} dB"
        )

    else:

        st.warning(
            "No visible samples available for antenna statistics."
        )

    if not antenna_data.empty:

        antenna_visualizer = AntennaVisualizer(
            antenna_data
        )

        st.subheader("Pointing Error vs Time")

        st.plotly_chart(
            antenna_visualizer.plot_pointing_error(),
            width="stretch"
        )

        st.subheader("Pointing Loss vs Time")

        st.plotly_chart(
            antenna_visualizer.plot_pointing_loss(),
            width="stretch"
        )

    # ======================================
    # F. LINK BUDGET PERFORMANCE
    # ======================================

    st.divider()

    st.header("9. Link Budget Performance")

    operational_data = link_data[
        link_data["link_available"] == True
    ]

    if len(operational_data) > 0:

        mean_received_power = (
            operational_data["received_power_dbm"].mean()
        )

        mean_snr = (
            operational_data["snr_db"].mean()
        )

        minimum_snr = (
            operational_data["snr_db"].min()
        )

        maximum_snr = (
            operational_data["snr_db"].max()
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Operational Samples",
            len(operational_data)
        )

        col2.metric(
            "Mean Received Power",
            f"{mean_received_power:.2f} dBm"
        )

        col3.metric(
            "Mean SNR",
            f"{mean_snr:.2f} dB"
        )

        col4.metric(
            "Minimum SNR",
            f"{minimum_snr:.2f} dB"
        )

        st.metric(
            "Maximum SNR",
            f"{maximum_snr:.2f} dB"
        )

    else:

        st.warning(
            "No operational link samples found. "
            "Check satellite visibility and elevation mask."
        )

    if not link_data.empty:

        link_visualizer = LinkVisualizer(link_data)

        st.subheader("Received Power vs Time")

        st.plotly_chart(
            link_visualizer.plot_received_power(),
            width="stretch"
        )

        st.subheader("SNR vs Time")

        st.plotly_chart(
            link_visualizer.plot_snr(),
            width="stretch"
        )

        st.subheader("Free Space Path Loss vs Time")

        st.plotly_chart(
            link_visualizer.plot_fspl(),
            width="stretch"
        )

    # ======================================
    # G. COMMUNICATION RELIABILITY
    # ======================================

    st.divider()

    st.header("10. Communication Reliability Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Overall Availability",
        f"{reliability_summary['overall_availability_percent']:.2f}%"
    )

    col2.metric(
        "Overall Outage Probability",
        f"{reliability_summary['overall_outage_probability_percent']:.2f}%"
    )

    snr_outage = reliability_summary[
        "snr_outage_probability_percent"
    ]

    col3.metric(
        "SNR Outage Probability",
        (
            f"{snr_outage:.2f}%"
            if snr_outage is not None
            else "N/A"
        )
    )

    st.write(
        "**SNR threshold:**",
        f"{reliability_summary['snr_threshold_db']:.2f} dB"
    )

    st.write(
        "**Reliable samples:**",
        reliability_summary["reliable_samples"]
    )

    st.write(
        "**Geometrically available samples:**",
        reliability_summary["geometric_available_samples"]
    )

    if not reliability_data.empty:

        reliability_visualizer = ReliabilityVisualizer(
            reliability_data
        )

        st.subheader("Communication Reliability vs Time")

        st.plotly_chart(
            reliability_visualizer.plot_availability(),
            width="stretch"
        )

        st.subheader("SNR Reliability vs Time")

        st.plotly_chart(
            reliability_visualizer.plot_snr_outage(),
            width="stretch"
        )

    # ======================================
    # H. DETAILED SIMULATION DATA
    # ======================================

    st.divider()

    st.header("11. Detailed Simulation Data")

    with st.expander("Satellite Tracking Data"):

        st.dataframe(
            data,
            width="stretch"
        )

    with st.expander("Antenna Pointing Results"):

        st.dataframe(
            antenna_data,
            width="stretch"
        )

    with st.expander("Link Budget Results"):

        st.dataframe(
            link_data,
            width="stretch"
        )

    with st.expander("Reliability Results"):

        st.dataframe(
            reliability_data,
            width="stretch"
        )

    # ======================================
    # I. CSV DOWNLOADS
    # ======================================

    st.divider()

    st.header("12. Download Simulation Results")

    download_col1, download_col2 = st.columns(2)

    with download_col1:

        st.download_button(
            label="Download Tracking CSV",
            data=data.to_csv(index=False),
            file_name="sotm_tracking_results.csv",
            mime="text/csv",
            width="stretch"
        )

        st.download_button(
            label="Download Antenna CSV",
            data=antenna_data.to_csv(index=False),
            file_name="sotm_antenna_results.csv",
            mime="text/csv",
            width="stretch"
        )

    with download_col2:

        st.download_button(
            label="Download Link Budget CSV",
            data=link_data.to_csv(index=False),
            file_name="sotm_link_results.csv",
            mime="text/csv",
            width="stretch"
        )

        st.download_button(
            label="Download Reliability CSV",
            data=reliability_data.to_csv(index=False),
            file_name="sotm_reliability_results.csv",
            mime="text/csv",
            width="stretch"
        )


# ==========================================
# 11. FOOTER
# ==========================================

st.divider()

st.caption(
    "SOTM Simulator | Integrated Satellite Communication Analysis"
)

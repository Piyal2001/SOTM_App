
import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime, date, time, timezone

from src.satellite import SatelliteOrbit
from src.moving_ground_station import MovingGroundStation
from src.moving_geometry import MovingSatelliteGeometry
from src.antenna import AntennaPointing
from src.link_budget import LinkBudget
from src.moving_tracking import MovingTerminalTracker


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("Moving Ground Terminal Simulation")
st.caption(
    "Satellite tracking, antenna pointing and link analysis "
    "for a moving ground terminal."
)

st.info(
    "This page uses a simplified constant-speed, constant-heading "
    "vehicle movement model. Replace the sample TLE with a current TLE "
    "before performing a new simulation."
)


# --------------------------------------------------
# SIDEBAR: SATELLITE INPUT
# --------------------------------------------------

st.sidebar.header("Satellite Configuration")

satellite_name = st.sidebar.text_input(
    "Satellite Name",
    value="Sample Satellite"
)

tle_line1 = st.sidebar.text_input(
    "TLE Line 1",
    value="1 03669U 69009A   26319.71221941  .00000089  00000+0  65893-4 0  9997"
)

tle_line2 = st.sidebar.text_input(
    "TLE Line 2",
    value="2 03669  88.4297 127.7148 1706012 302.3359  42.3553 11.30458770376897"
)


# --------------------------------------------------
# SIDEBAR: VEHICLE INPUT
# --------------------------------------------------

st.sidebar.header("Moving Ground Terminal")

vehicle_name = st.sidebar.text_input(
    "Vehicle Name",
    value="Moving Vehicle"
)

start_latitude = st.sidebar.number_input(
    "Starting Latitude (degrees)",
    min_value=-90.0,
    max_value=90.0,
    value=22.5726,
    format="%.6f"
)

start_longitude = st.sidebar.number_input(
    "Starting Longitude (degrees)",
    min_value=-180.0,
    max_value=180.0,
    value=88.3639,
    format="%.6f"
)

vehicle_altitude = st.sidebar.number_input(
    "Vehicle Altitude (km)",
    min_value=-0.5,
    max_value=20.0,
    value=0.01,
    format="%.3f"
)

vehicle_speed = st.sidebar.number_input(
    "Vehicle Speed (km/h)",
    min_value=0.0,
    max_value=300.0,
    value=60.0,
    step=5.0
)

vehicle_heading = st.sidebar.number_input(
    "Vehicle Heading (degrees)",
    min_value=0.0,
    max_value=360.0,
    value=90.0,
    step=5.0
)

st.sidebar.caption(
    "Heading: 0° North, 90° East, 180° South, 270° West."
)


# --------------------------------------------------
# SIDEBAR: SIMULATION SETTINGS
# --------------------------------------------------

st.sidebar.header("Simulation Settings")

simulation_date = st.sidebar.date_input(
    "Simulation Date (UTC)",
    value=date.today()
)

simulation_time = st.sidebar.time_input(
    "Simulation Start Time (UTC)",
    value=time(10, 0)
)

duration_minutes = st.sidebar.number_input(
    "Simulation Duration (minutes)",
    min_value=1,
    max_value=360,
    value=30
)

interval_seconds = st.sidebar.selectbox(
    "Sampling Interval (seconds)",
    options=[5, 10, 15, 30, 60],
    index=3
)

elevation_mask = st.sidebar.number_input(
    "Elevation Mask (degrees)",
    min_value=0.0,
    max_value=90.0,
    value=10.0,
    step=1.0
)


# --------------------------------------------------
# SIDEBAR: ANTENNA SETTINGS
# --------------------------------------------------

st.sidebar.header("Antenna Settings")

beamwidth = st.sidebar.number_input(
    "Antenna Beamwidth (degrees)",
    min_value=0.1,
    max_value=180.0,
    value=2.0
)

azimuth_offset = st.sidebar.number_input(
    "Azimuth Offset (degrees)",
    min_value=-10.0,
    max_value=10.0,
    value=0.5
)

elevation_offset = st.sidebar.number_input(
    "Elevation Offset (degrees)",
    min_value=-10.0,
    max_value=10.0,
    value=0.5
)


# --------------------------------------------------
# SIDEBAR: LINK BUDGET SETTINGS
# --------------------------------------------------

st.sidebar.header("Link Budget Settings")

frequency = st.sidebar.number_input(
    "Frequency (GHz)",
    min_value=0.1,
    max_value=100.0,
    value=12.0
)

tx_power = st.sidebar.number_input(
    "Transmit Power (dBm)",
    value=40.0
)

tx_gain = st.sidebar.number_input(
    "Transmit Antenna Gain (dBi)",
    value=30.0
)

rx_gain = st.sidebar.number_input(
    "Receive Antenna Gain (dBi)",
    value=35.0
)

bandwidth = st.sidebar.number_input(
    "Bandwidth (MHz)",
    min_value=0.001,
    max_value=1000.0,
    value=10.0
)

noise_figure = st.sidebar.number_input(
    "Noise Figure (dB)",
    min_value=0.0,
    max_value=50.0,
    value=2.0
)

other_losses = st.sidebar.number_input(
    "Other Losses (dB)",
    min_value=0.0,
    max_value=100.0,
    value=2.0
)


# --------------------------------------------------
# RUN SIMULATION
# --------------------------------------------------

run_simulation = st.sidebar.button(
    "Run Moving Terminal Simulation",
    type="primary",
    use_container_width=True
)


if run_simulation:

    try:

        with st.spinner("Running moving-terminal simulation..."):

            # 1. Simulation start time
            start_datetime = datetime.combine(
                simulation_date,
                simulation_time
            ).replace(tzinfo=timezone.utc)

            # 2. Satellite orbit
            satellite = SatelliteOrbit(
                satellite_name,
                tle_line1.strip(),
                tle_line2.strip()
            )

            # 3. Moving ground terminal
            moving_station = MovingGroundStation(
                name=vehicle_name,
                start_latitude=start_latitude,
                start_longitude=start_longitude,
                speed_kmh=vehicle_speed,
                heading_deg=vehicle_heading,
                start_time=start_datetime,
                altitude_km=vehicle_altitude
            )

            # 4. Moving satellite geometry
            geometry = MovingSatelliteGeometry(satellite)

            tracking_data = geometry.generate_tracking_data(
                moving_ground_station=moving_station,
                start_time=start_datetime,
                duration_minutes=int(duration_minutes),
                interval_seconds=int(interval_seconds)
            )

            # 5. Antenna model
            antenna = AntennaPointing(
                beamwidth_deg=beamwidth,
                azimuth_offset_deg=azimuth_offset,
                elevation_offset_deg=elevation_offset
            )

            # 6. Link budget model
            link_budget = LinkBudget(
                frequency_ghz=frequency,
                transmit_power_dbm=tx_power,
                transmit_gain_dbi=tx_gain,
                receive_gain_dbi=rx_gain,
                bandwidth_mhz=bandwidth,
                noise_figure_db=noise_figure,
                other_losses_db=other_losses
            )

            # 7. Moving terminal tracker
            tracker = MovingTerminalTracker(
                antenna=antenna,
                link_budget=link_budget,
                elevation_mask_deg=elevation_mask
            )

            processed_results = tracker.process_tracking_data(
                tracking_data
            )

            antenna_results = processed_results["antenna_results"]
            link_results = processed_results["link_results"]

            # 8. Save results in session state
            st.session_state["moving_simulation_results"] = {
                "tracking_data": tracking_data,
                "antenna_results": antenna_results,
                "link_results": link_results,
                "vehicle_name": vehicle_name,
                "satellite_name": satellite_name,
                "start_datetime": start_datetime
            }

        st.success("Moving-terminal simulation completed successfully!")

    except Exception as error:

        st.error(f"Simulation failed: {error}")


# --------------------------------------------------
# DISPLAY SIMULATION RESULTS
# --------------------------------------------------

results = st.session_state.get("moving_simulation_results")

if results is not None:

    tracking_data = results["tracking_data"]
    antenna_results = results["antenna_results"]
    link_results = results["link_results"]

    st.divider()
    st.header("Simulation Dashboard")

    # Operational samples
    operational_data = link_results[
        link_results["link_available"] == True
    ].copy()

    total_samples = len(tracking_data)
    operational_samples = len(operational_data)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Samples",
        total_samples
    )

    col2.metric(
        "Operational Samples",
        operational_samples
    )

    col3.metric(
        "Maximum Elevation",
        f"{tracking_data['elevation_deg'].max():.2f}°"
    )

    col4.metric(
        "Vehicle Distance",
        f"{tracking_data['distance_travelled_km'].iloc[-1]:.2f} km"
    )

    col5, col6, col7 = st.columns(3)

    if not operational_data.empty:

        col5.metric(
            "Mean SNR",
            f"{operational_data['snr_db'].mean():.2f} dB"
        )

        col6.metric(
            "Mean Received Power",
            f"{operational_data['received_power_dbm'].mean():.2f} dBm"
        )

        col7.metric(
            "Mean Pointing Error",
            f"{operational_data['pointing_error_deg'].mean():.3f}°"
        )

    else:

        col5.metric("Mean SNR", "N/A")
        col6.metric("Mean Received Power", "N/A")
        col7.metric("Mean Pointing Error", "N/A")

    st.divider()

    # --------------------------------------------------
    # VEHICLE MOVEMENT
    # --------------------------------------------------

    st.subheader("1. Vehicle Movement")

    fig = px.line(
        tracking_data,
        x="time_utc",
        y="vehicle_latitude_deg",
        title="Vehicle Latitude vs Time"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
         tracking_data,
        x="time_utc",
        y="vehicle_longitude_deg",
        title="Vehicle Longitude vs Time"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # SATELLITE TRACKING
    # --------------------------------------------------

    st.subheader("2. Satellite Tracking")

    fig = px.line(
        tracking_data,
        x="time_utc",
        y="azimuth_deg",
        title="Satellite Azimuth vs Time"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        tracking_data,
        x="time_utc",
        y="elevation_deg",
        title="Satellite Elevation vs Time"
    )

    fig.add_hline(
        y=elevation_mask,
        line_dash="dash",
        annotation_text="Elevation Mask"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        tracking_data,
        x="time_utc",
        y="slant_range_km",
        title="Satellite Slant Range vs Time"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # ANTENNA PERFORMANCE
    # --------------------------------------------------

    st.subheader("3. Antenna Pointing Performance")

    fig = px.line(
        antenna_results,
        x="time_utc",
        y="pointing_error_deg",
        title="Antenna Pointing Error vs Time"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        antenna_results,
        x="time_utc",
        y="pointing_loss_db",
        title="Antenna Pointing Loss vs Time"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # LINK PERFORMANCE
    # --------------------------------------------------

    st.subheader("4. Communication Link Performance")

    if not operational_data.empty:

        fig = px.line(
            operational_data,
            x="time_utc",
            y="snr_db",
            title="Signal-to-Noise Ratio vs Time"
        )

        st.plotly_chart(fig, use_container_width=True)

        fig = px.line(
            operational_data,
            x="time_utc",
            y="received_power_dbm",
            title="Received Power vs Time"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:

        st.warning(
            "No samples are above the selected elevation mask. "
            "Link performance cannot be displayed for this simulation."
        )

    # --------------------------------------------------
    # DATA TABLES
    # --------------------------------------------------

    st.divider()
    st.subheader("5. Simulation Data")

    with st.expander("Satellite and Vehicle Tracking Data"):

        st.dataframe(
            tracking_data,
            use_container_width=True
        )

    with st.expander("Antenna Pointing Results"):

        st.dataframe(
            antenna_results,
            use_container_width=True
        )

    with st.expander("Communication Link Results"):

        st.dataframe(
            link_results,
            use_container_width=True
        )

    # --------------------------------------------------
    # DOWNLOAD RESULTS
    # --------------------------------------------------

    st.divider()
    st.subheader("6. Download Simulation Results")

    col1, col2, col3 = st.columns(3)

    col1.download_button(
        "Download Tracking CSV",
        tracking_data.to_csv(index=False),
        file_name="moving_tracking_results.csv",
        mime="text/csv"
    )

    col2.download_button(
        "Download Antenna CSV",
        antenna_results.to_csv(index=False),
        file_name="moving_antenna_results.csv",
        mime="text/csv"
    )

    col3.download_button(
        "Download Link CSV",
        link_results.to_csv(index=False),
        file_name="moving_link_results.csv",
        mime="text/csv"
    )

else:

    st.info(
        "Configure the satellite, moving vehicle and simulation "
        "settings in the sidebar, then click "
        "'Run Moving Terminal Simulation'."
    )

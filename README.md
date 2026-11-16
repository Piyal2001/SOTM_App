
# Interactive Satellite Simulation Web Application

A Python-based interactive web application developed using Streamlit for satellite tracking, antenna pointing analysis, communication link budget evaluation, and reliability assessment.

## Features

- Satellite orbit input using Two-Line Element (TLE) data.
- Satellite tracking and pass prediction.
- Ground station configuration.
- Moving terminal simulation.
- Azimuth, elevation, and slant-range calculations.
- Antenna pointing error and pointing loss analysis.
- Free-space path loss and received power calculations.
- Signal-to-noise ratio (SNR) analysis.
- Communication reliability and availability assessment.
- Interactive visualizations.
- CSV export of simulation results.

## Technologies Used

- Python
- Streamlit
- NumPy
- Pandas
- Plotly
- Skyfield
- SGP4
- Matplotlib

## Installation

Clone the repository:

```bash
git clone YOUR_PRIVATE_REPOSITORY_URL
```

Navigate into the project folder:

```bash
cd SOTM_Paper2_App
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## Project Structure

```text
SOTM_Paper2_App/
├── app.py
├── pages/
├── src/
├── data/
│   └── TLE/
├── assets/
├── results/
├── requirements.txt
└── README.md
```

## Note

The application is intended for simulation and educational purposes. Simulation results depend on the supplied orbital data and configuration parameters.

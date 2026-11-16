
import math


class LinkBudget:

    def __init__(
        self,
        frequency_ghz=12.0,
        transmit_power_dbm=40.0,
        transmit_gain_dbi=30.0,
        receive_gain_dbi=35.0,
        bandwidth_mhz=10.0,
        noise_figure_db=2.0,
        other_losses_db=2.0
    ):

        self.frequency_ghz = frequency_ghz
        self.transmit_power_dbm = transmit_power_dbm
        self.transmit_gain_dbi = transmit_gain_dbi
        self.receive_gain_dbi = receive_gain_dbi
        self.bandwidth_mhz = bandwidth_mhz
        self.noise_figure_db = noise_figure_db
        self.other_losses_db = other_losses_db

        self.validate_parameters()

    # ======================================
    # 1. VALIDATE PARAMETERS
    # ======================================

    def validate_parameters(self):

        if self.frequency_ghz <= 0:
            raise ValueError("Frequency must be positive.")

        if self.bandwidth_mhz <= 0:
            raise ValueError("Bandwidth must be positive.")

        if self.noise_figure_db < 0:
            raise ValueError("Noise figure cannot be negative.")

        if self.other_losses_db < 0:
            raise ValueError("Other losses cannot be negative.")

    # ======================================
    # 2. FREE SPACE PATH LOSS
    # ======================================

    def calculate_fspl(self, distance_km):

        if distance_km <= 0:
            raise ValueError("Distance must be positive.")

        fspl = (
            92.45
            + 20 * math.log10(self.frequency_ghz)
            + 20 * math.log10(distance_km)
        )

        return fspl

    # ======================================
    # 3. RECEIVED SIGNAL POWER
    # ======================================

    def calculate_received_power(
        self,
        distance_km,
        pointing_loss_db
    ):

        fspl = self.calculate_fspl(distance_km)

        received_power = (
            self.transmit_power_dbm
            + self.transmit_gain_dbi
            + self.receive_gain_dbi
            - fspl
            - self.other_losses_db
            - pointing_loss_db
        )

        return received_power

    # ======================================
    # 4. NOISE POWER
    # ======================================

    def calculate_noise_power(self):

        bandwidth_hz = self.bandwidth_mhz * 1e6

        noise_power = (
            -174
            + 10 * math.log10(bandwidth_hz)
            + self.noise_figure_db
        )

        return noise_power

    # ======================================
    # 5. SIGNAL-TO-NOISE RATIO
    # ======================================

    def calculate_snr(
        self,
        received_power_dbm
    ):

        noise_power_dbm = self.calculate_noise_power()

        snr_db = received_power_dbm - noise_power_dbm

        return snr_db

    # ======================================
    # 6. COMPLETE LINK BUDGET
    # ======================================

    def analyze(
        self,
        distance_km,
        pointing_loss_db
    ):

        fspl = self.calculate_fspl(distance_km)

        received_power = self.calculate_received_power(
            distance_km,
            pointing_loss_db
        )

        noise_power = self.calculate_noise_power()

        snr = self.calculate_snr(received_power)

        return {
            "distance_km": distance_km,
            "frequency_ghz": self.frequency_ghz,
            "fspl_db": fspl,
            "received_power_dbm": received_power,
            "noise_power_dbm": noise_power,
            "pointing_loss_db": pointing_loss_db,
            "snr_db": snr
        }

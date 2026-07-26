"""
Real-time Grid Carbon Intensity & Tariff Simulation Service
Provides dynamic grid emission factors (gCO2/kWh) and time-of-use (TOU) electricity pricing ($/kWh).
"""

import math

class GridIntensityService:
    def __init__(self):
        # Base grid emissions (g CO2 / kWh)
        self.base_carbon_intensity = 350.0  # gCO2/kWh average grid
        # Peak pricing structure ($/kWh)
        self.base_electricity_rate = 0.15   # $0.15/kWh off-peak

    def get_grid_state(self, hour: float) -> dict:
        """
        Calculates dynamic grid carbon intensity and electricity tariff based on time of day.
        :param hour: Hour of day (0.0 to 24.0)
        :return: dict with carbon_intensity_g_kwh, tariff_usd_kwh, is_peak_carbon, is_peak_pricing
        """
        # Peak grid carbon intensity typically occurs during evening ramp (16:00 - 21:00) when fossil peaker plants run
        # Solar generation drops carbon intensity during midday (10:00 - 15:00)
        
        # Diurnal carbon factor curve
        if 10.0 <= hour <= 15.0:
            carbon_factor = 0.65  # Renewable high solar yield -> 227 gCO2/kWh
        elif 16.0 <= hour <= 21.0:
            carbon_factor = 1.60  # Fossil peaker plant ramp -> 560 gCO2/kWh
        else:
            carbon_factor = 1.00  # Baseline -> 350 gCO2/kWh

        carbon_intensity = self.base_carbon_intensity * carbon_factor

        # Dynamic Time-Of-Use Tariff
        if 14.0 <= hour <= 20.0:
            tariff = 0.35  # Peak pricing $0.35/kWh
            is_peak_pricing = True
        elif 8.0 <= hour <= 14.0:
            tariff = 0.22  # Mid-peak $0.22/kWh
            is_peak_pricing = False
        else:
            tariff = 0.12  # Off-peak $0.12/kWh
            is_peak_pricing = False

        return {
            "hour": round(hour, 2),
            "carbon_intensity_g_kwh": round(carbon_intensity, 1),
            "tariff_usd_kwh": round(tariff, 3),
            "is_peak_carbon": carbon_factor > 1.2,
            "is_peak_pricing": is_peak_pricing,
            "grid_status": "HIGH CARBON (PEAKER PLANTS)" if carbon_factor > 1.2 else ("LOW CARBON (CLEAN SOLAR)" if carbon_factor < 0.8 else "NORMAL GRID")
        }

if __name__ == "__main__":
    service = GridIntensityService()
    print("12:00 Grid State:", service.get_grid_state(12.0))
    print("18:00 Grid State:", service.get_grid_state(18.0))

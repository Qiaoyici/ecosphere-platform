# config.py
"""Configuration settings and carbon multipliers for the EcoSphere Platform.

Contains all carbon emission factors, security VM loads, limits,
thresholds, and relatable carbon offset conversions.
"""

# Grid conversion factor (kg CO2 per kWh)
GRID_CO2_FACTOR = 0.82

# Time conversion constants
YEARLY_DAYS = 365.25
YEARLY_MONTHS = 12

# 🍃 Personal Emission Multipliers (kg CO2 per unit)
CAR_EMISSION_FACTOR = 0.18        # Driving typical gasoline car
FLIGHT_EMISSION_FACTOR = 90.0      # Commercial passenger jet flight hour
ELECTRICITY_EMISSION_FACTOR = 0.82  # Average grid factor
WASTE_EMISSION_FACTOR = 0.5        # Landfill waste per kg

# Daily dietary carbon weights (kg CO2 per day)
DIET_DAILY_FACTORS = {
    "beef_heavy": 7.2,
    "high_meat": 3.3,
    "poultry_fish": 3.8,
    "low_meat": 2.5,
    "vegetarian": 1.7,
    "plant_based_meat": 1.9,
    "vegan": 1.5,
    "locally_sourced_veg": 1.3
}
DEFAULT_DIET_FACTOR = 2.5

# 💻 GreenSec IT Emission Factors (kWh per unit)
# Cryptographic Operations (kWh per 1 Million Operations)
CRYPTO_KWH_PER_MILLION = {
    "rsa4096": 0.08,
    "rsa2048": 0.02,
    "ecc256": 0.005,
}
DEFAULT_CRYPTO_KWH = 0.08

# SIEM Logging Storage (kg CO2 per GB per month)
SIEM_STORAGE_CO2_PER_GB_MONTH = {
    "hot_storage": 0.015,
    "cold_archive": 0.002,
}
DEFAULT_STORAGE_CO2 = 0.015

# Vulnerability Security Scans (kWh per scan)
SCAN_KWH_PER_RUN = {
    "full_dast": 0.50,
    "targeted_sast": 0.02,
}
DEFAULT_SCAN_KWH = 0.50

# Dedicated VM Host Security Agents (kWh per hour)
AGENT_KWH_PER_HOUR = {
    "heavy_agent": 0.05,
    "light_kernel": 0.008
}
DEFAULT_AGENT_KWH = 0.05

# 🌳 Relatable Equivalencies Conversion Divisors
TREES_OFFSET_DIVISOR = 22.0          # kg CO2 offset by mature tree yearly
SMARTPHONE_CHARGE_DIVISOR = 0.00656   # kg CO2 per charge
FLIGHT_EQUIVALENT_DIVISOR = 90.0      # Passenger flight hour share
HOUSEHOLD_MONTH_DIVISOR = 123.0       # Avg household monthly power footprint

# 🛡️ Safety & Validation Input Thresholds (Personal)
CAR_KM_MAX = 1000000.0
FLIGHT_HOURS_MAX = 1000.0
ELECTRICITY_KWH_MAX = 100000.0
WASTE_KG_MAX = 50000.0

# 🛡️ Safety & Validation Input Thresholds (GreenSec)
CRYPTO_OPS_MAX = 100000.0
LOG_SIZE_MAX = 1000000.0
SCAN_RUNS_MAX = 100000.0
SERVER_HOURS_MAX = 744000.0

import logging
from typing import Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


# Traditional/Everyday Carbon Emission Factors (kg CO2 per unit)
EMISSION_FACTORS_PERSONAL = {
    "car_per_km": 0.18,        # Driving typical gasoline car
    "flight_per_hour": 90.0,    # Flying commercial passenger jet (~90 kg CO2 per hour passenger share)
    "electricity_per_kwh": 0.82,# Grid electricity average
    "waste_per_kg": 0.5,        # Waste disposed in landfill
    "diet_daily": {
        "beef_heavy": 7.2,
        "high_meat": 3.3,
        "poultry_fish": 3.8,
        "low_meat": 2.5,
        "vegetarian": 1.7,
        "plant_based_meat": 1.9,
        "vegan": 1.5,
        "locally_sourced_veg": 1.3
    }
}

# GreenSec IT Carbon Emission Factors (kWh per unit)
# Powered by average grid factor of 0.82 kg CO2 / kWh
GRID_CO2_FACTOR = 0.82

EMISSION_FACTORS_GREENSEC = {
    # Cryptographic Operations (kWh per 1 Million Operations)
    "crypto_kwh_per_million": {
        "rsa4096": 0.08,        # Energy heavy
        "rsa2048": 0.02,
        "ecc256": 0.005,        # Energy light
    },
    # SIEM Logging Storage (kg CO2 per GB per month)
    "siem_storage_co2_per_gb_month": {
        "hot_storage": 0.015,   # High-availability hot storage (SSD, replication)
        "cold_archive": 0.002,  # Compressed, tiered cold archive
    },
    # Vulnerability Security Scans (kWh per scan)
    "scan_kwh_per_run": {
        "full_dast": 0.50,      # Dynamic Application Security Scan (Long running, continuous environment traffic)
        "targeted_sast": 0.02,  # Static Application Security Scan (Incremental, quick analysis)
    },
    # Dedicated VM Host Security Agents (kWh per hour)
    "agent_kwh_per_hour": {
        "heavy_agent": 0.05,    # Multi-agent active scanning agent
        "light_kernel": 0.008   # EBPF kernel-level passive sensor
    }
}

def _calculate_car_co2(car_km: float) -> float:
    return car_km * EMISSION_FACTORS_PERSONAL["car_per_km"]


def _calculate_flight_co2(flight_hours: float) -> float:
    return flight_hours * EMISSION_FACTORS_PERSONAL["flight_per_hour"]


def _calculate_diet_co2(diet_type: str) -> float:
    factor = EMISSION_FACTORS_PERSONAL["diet_daily"].get(diet_type, 2.5)
    return factor * 365.25


def _calculate_electricity_co2(kwh: float) -> float:
    return kwh * EMISSION_FACTORS_PERSONAL["electricity_per_kwh"]


def _calculate_waste_co2(kg: float) -> float:
    return kg * EMISSION_FACTORS_PERSONAL["waste_per_kg"]


@lru_cache(maxsize=128)
def calculate_personal_footprint(
    car_km_per_year: float,
    flight_hours_per_year: float,
    diet_type: str,
    electricity_kwh_per_year: float,
    waste_kg_per_year: float,
) -> Dict[str, Any]:
    """Calculates yearly personal carbon emissions by category in kg CO2."""
    logger.info(
        f"calculate_personal_footprint called: "
        f"car_km={car_km_per_year}, diet={diet_type}"
    )
    car_co2 = _calculate_car_co2(car_km_per_year)
    flight_co2 = _calculate_flight_co2(flight_hours_per_year)
    diet_co2 = _calculate_diet_co2(diet_type)
    electricity_co2 = _calculate_electricity_co2(electricity_kwh_per_year)
    waste_co2 = _calculate_waste_co2(waste_kg_per_year)

    total = car_co2 + flight_co2 + diet_co2 + electricity_co2 + waste_co2

    return {
        "breakdown": {
            "transportation": round(car_co2 + flight_co2, 1),
            "diet": round(diet_co2, 1),
            "energy": round(electricity_co2, 1),
            "waste": round(waste_co2, 1),
        },
        "total_kg": round(total, 1),
        "components": {
            "car_co2": round(car_co2, 1),
            "flight_co2": round(flight_co2, 1),
            "diet_co2": round(diet_co2, 1),
            "electricity_co2": round(electricity_co2, 1),
            "waste_co2": round(waste_co2, 1),
        },
    }


def _calculate_crypto_co2(ops_millions: float, crypto_type: str) -> float:
    factor = EMISSION_FACTORS_GREENSEC["crypto_kwh_per_million"].get(
        crypto_type, 0.08
    )
    return ops_millions * factor * 12 * GRID_CO2_FACTOR


def _calculate_storage_co2(gb: float, storage_type: str) -> float:
    factor = EMISSION_FACTORS_GREENSEC["siem_storage_co2_per_gb_month"].get(
        storage_type, 0.015
    )
    return gb * factor * 12


def _calculate_scan_co2(runs: float, scan_type: str) -> float:
    factor = EMISSION_FACTORS_GREENSEC["scan_kwh_per_run"].get(scan_type, 0.5)
    return runs * factor * 12 * GRID_CO2_FACTOR


def _calculate_agent_co2(hours: float, agent_type: str) -> float:
    factor = EMISSION_FACTORS_GREENSEC["agent_kwh_per_hour"].get(
        agent_type, 0.05
    )
    return hours * factor * 12 * GRID_CO2_FACTOR


def _calculate_optimized_greensec_total(
    ops: float, gb: float, runs: float, hours: float
) -> float:
    opt_crypto = (
        ops
        * EMISSION_FACTORS_GREENSEC["crypto_kwh_per_million"]["ecc256"]
        * 12
        * GRID_CO2_FACTOR
    )
    opt_storage = (
        gb
        * EMISSION_FACTORS_GREENSEC["siem_storage_co2_per_gb_month"]["cold_archive"]
        * 12
    )
    opt_scan = (
        runs
        * EMISSION_FACTORS_GREENSEC["scan_kwh_per_run"]["targeted_sast"]
        * 12
        * GRID_CO2_FACTOR
    )
    opt_agent = (
        hours
        * EMISSION_FACTORS_GREENSEC["agent_kwh_per_hour"]["light_kernel"]
        * 12
        * GRID_CO2_FACTOR
    )
    return opt_crypto + opt_storage + opt_scan + opt_agent


@lru_cache(maxsize=128)
def calculate_greensec_footprint(
    crypto_ops_millions: float,
    crypto_type: str,
    log_size_gb: float,
    log_storage_type: str,
    scan_runs_per_month: float,
    scan_type: str,
    server_hours_per_month: float,
    agent_type: str,
) -> Dict[str, Any]:
    """Calculates yearly digital security carbon emissions in kg CO2."""
    logger.info(
        f"calculate_greensec_footprint called: "
        f"crypto_ops={crypto_ops_millions}, crypto_type={crypto_type}"
    )
    crypto_co2 = _calculate_crypto_co2(crypto_ops_millions, crypto_type)
    storage_co2 = _calculate_storage_co2(log_size_gb, log_storage_type)
    scan_co2 = _calculate_scan_co2(scan_runs_per_month, scan_type)
    agent_co2 = _calculate_agent_co2(server_hours_per_month, agent_type)

    total = crypto_co2 + storage_co2 + scan_co2 + agent_co2

    optimized_total = _calculate_optimized_greensec_total(
        crypto_ops_millions,
        log_size_gb,
        scan_runs_per_month,
        server_hours_per_month,
    )
    potential_savings = max(0.0, total - optimized_total)

    return {
        "breakdown": {
            "cryptography": round(crypto_co2, 1),
            "log_storage": round(storage_co2, 1),
            "vulnerability_scans": round(scan_co2, 1),
            "host_agents": round(agent_co2, 1),
        },
        "total_kg": round(total, 1),
        "potential_savings_kg": round(potential_savings, 1),
        "components": {
            "crypto_co2": round(crypto_co2, 1),
            "storage_co2": round(storage_co2, 1),
            "scan_co2": round(scan_co2, 1),
            "agent_co2": round(agent_co2, 1),
        },
    }


@lru_cache(maxsize=128)
def get_relatable_equivalencies(co2_kg: float) -> Dict[str, Any]:
    """Translates raw CO2 kg into relatable physical metrics."""
    logger.info(f"get_relatable_equivalencies called: co2_kg={co2_kg}")
    trees = co2_kg / 22.0
    charges = co2_kg / 0.00656
    flights = co2_kg / 90.0
    household_months = co2_kg / 123.0

    return {
        "trees_planted": round(trees, 1),
        "smartphone_charges": round(charges, 0),
        "delhi_mumbai_flights": round(flights, 1),
        "household_electricity_months": round(household_months, 1),
    }


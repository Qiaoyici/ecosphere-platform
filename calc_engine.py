import logging
from typing import Dict, Any
from functools import lru_cache
import copy
import config

logger = logging.getLogger(__name__)


def _calculate_car_co2(car_km: float) -> float:
    return car_km * config.CAR_EMISSION_FACTOR


def _calculate_flight_co2(flight_hours: float) -> float:
    return flight_hours * config.FLIGHT_EMISSION_FACTOR


def _calculate_diet_co2(diet_type: str) -> float:
    factor = config.DIET_DAILY_FACTORS.get(
        diet_type, config.DEFAULT_DIET_FACTOR
    )
    return factor * config.YEARLY_DAYS


def _calculate_electricity_co2(kwh: float) -> float:
    return kwh * config.ELECTRICITY_EMISSION_FACTOR


def _calculate_waste_co2(kg: float) -> float:
    return kg * config.WASTE_EMISSION_FACTOR


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

    return copy.deepcopy(
        {
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
    )


def _calculate_crypto_co2(ops_millions: float, crypto_type: str) -> float:
    factor = config.CRYPTO_KWH_PER_MILLION.get(
        crypto_type, config.DEFAULT_CRYPTO_KWH
    )
    return ops_millions * factor * config.YEARLY_MONTHS * config.GRID_CO2_FACTOR


def _calculate_storage_co2(gb: float, storage_type: str) -> float:
    factor = config.SIEM_STORAGE_CO2_PER_GB_MONTH.get(
        storage_type, config.DEFAULT_STORAGE_CO2
    )
    return gb * factor * config.YEARLY_MONTHS


def _calculate_scan_co2(runs: float, scan_type: str) -> float:
    factor = config.SCAN_KWH_PER_RUN.get(scan_type, config.DEFAULT_SCAN_KWH)
    return runs * factor * config.YEARLY_MONTHS * config.GRID_CO2_FACTOR


def _calculate_agent_co2(hours: float, agent_type: str) -> float:
    factor = config.AGENT_KWH_PER_HOUR.get(agent_type, config.DEFAULT_AGENT_KWH)
    return hours * factor * config.YEARLY_MONTHS * config.GRID_CO2_FACTOR


def _calculate_optimized_greensec_total(
    ops: float, gb: float, runs: float, hours: float
) -> float:
    opt_crypto = (
        ops
        * config.CRYPTO_KWH_PER_MILLION["ecc256"]
        * config.YEARLY_MONTHS
        * config.GRID_CO2_FACTOR
    )
    opt_storage = (
        gb
        * config.SIEM_STORAGE_CO2_PER_GB_MONTH["cold_archive"]
        * config.YEARLY_MONTHS
    )
    opt_scan = (
        runs
        * config.SCAN_KWH_PER_RUN["targeted_sast"]
        * config.YEARLY_MONTHS
        * config.GRID_CO2_FACTOR
    )
    opt_agent = (
        hours
        * config.AGENT_KWH_PER_HOUR["light_kernel"]
        * config.YEARLY_MONTHS
        * config.GRID_CO2_FACTOR
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

    return copy.deepcopy(
        {
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
    )


@lru_cache(maxsize=128)
def get_relatable_equivalencies(co2_kg: float) -> Dict[str, Any]:
    """Translates raw CO2 kg into relatable physical metrics."""
    logger.info(f"get_relatable_equivalencies called: co2_kg={co2_kg}")
    trees = co2_kg / config.TREES_OFFSET_DIVISOR
    charges = co2_kg / config.SMARTPHONE_CHARGE_DIVISOR
    flights = co2_kg / config.FLIGHT_EQUIVALENT_DIVISOR
    household_months = co2_kg / config.HOUSEHOLD_MONTH_DIVISOR

    return copy.deepcopy(
        {
            "trees_planted": round(trees, 1),
            "smartphone_charges": round(charges, 0),
            "delhi_mumbai_flights": round(flights, 1),
            "household_electricity_months": round(household_months, 1),
        }
    )

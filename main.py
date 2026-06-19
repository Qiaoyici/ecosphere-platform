import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
import config
import calc_engine
import security_utils

# Configure logging at INFO level
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EcoSphere: Enterprise Carbon & GreenSec Risk Platform",
    version="1.0.0",
    description="Backend API calculations, security state verification, and audit logs."
)

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Enable response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ----------------- GLOBAL EXCEPTION HANDLERS -----------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    logger.error(f"Request validation failed: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error": str(exc.errors()), "status": 422}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        logger.error(f"HTTP error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status": exc.status_code}
        )
    logger.error(f"Unhandled system error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected server error occurred.", "status": 500}
    )

# ----------------- PYDANTIC REQUEST MODELS -----------------

class PersonalCalcRequest(BaseModel):
    car_km_per_year: float = Field(
        default=0.0,
        ge=0.0,
        le=config.CAR_KM_MAX,
        description="Annual driving distance in km",
    )
    flight_hours_per_year: float = Field(
        default=0.0,
        ge=0.0,
        le=config.FLIGHT_HOURS_MAX,
        description="Annual flight hours",
    )
    diet_type: Literal[
        "beef_heavy",
        "high_meat",
        "poultry_fish",
        "low_meat",
        "vegetarian",
        "plant_based_meat",
        "vegan",
        "locally_sourced_veg",
    ] = Field(default="vegetarian", description="Diet preference")
    electricity_kwh_per_year: float = Field(
        default=0.0,
        ge=0.0,
        le=config.ELECTRICITY_KWH_MAX,
        description="Annual electricity usage in kWh",
    )
    waste_kg_per_year: float = Field(
        default=0.0,
        ge=0.0,
        le=config.WASTE_KG_MAX,
        description="Annual waste generated in kg",
    )


class GreenSecCalcRequest(BaseModel):
    crypto_ops_millions: float = Field(
        default=0.0,
        ge=0.0,
        le=config.CRYPTO_OPS_MAX,
        description="Millions of operations",
    )
    crypto_type: Literal["rsa4096", "rsa2048", "ecc256"] = Field(
        default="ecc256", description="Algorithm type"
    )
    log_size_gb: float = Field(
        default=0.0,
        ge=0.0,
        le=config.LOG_SIZE_MAX,
        description="Size of SIEM logging in GB",
    )
    log_storage_type: Literal["hot_storage", "cold_archive"] = Field(
        default="cold_archive", description="Storage level"
    )
    scan_runs_per_month: float = Field(
        default=0.0,
        ge=0.0,
        le=config.SCAN_RUNS_MAX,
        description="Security scans run per month",
    )
    scan_type: Literal["full_dast", "targeted_sast"] = Field(
        default="targeted_sast", description="Scan type"
    )
    server_hours_per_month: float = Field(
        default=0.0,
        ge=0.0,
        le=config.SERVER_HOURS_MAX,
        description="Server hosting hours per month",
    )
    agent_type: Literal["heavy_agent", "light_kernel"] = Field(
        default="light_kernel", description="Host agent"
    )


class StateSignRequest(BaseModel):
    state: Dict[str, Any] = Field(..., description="Client-side JSON state object")


class StateVerifyRequest(BaseModel):
    payload: str = Field(..., max_length=10000, description="Base64 payload string")
    signature: str = Field(..., max_length=128, description="HMAC signature hash")

# ----------------- API ENDPOINTS -----------------

@app.post("/api/calculate/personal")
async def calculate_personal(req: PersonalCalcRequest) -> Dict[str, Any]:
    """Calculates personal carbon footprint from request data asynchronously.

    Addresses the root challenge of invisible lifestyle emissions by
    translating everyday choices (driving, flights, diet, utilities)
    into real-time carbon equivalencies, helping users understand
    their environmental exposure.

    Args:
        req: Personal carbon footprint parameters.

    Returns:
        A dictionary containing the detailed breakdown and equivalencies.
    """
    logger.info(f"calculate_personal endpoint called with diet_type={req.diet_type}")
    car_km = security_utils.validate_numeric_input(
        req.car_km_per_year, 0, config.CAR_KM_MAX
    )
    flights = security_utils.validate_numeric_input(
        req.flight_hours_per_year, 0, config.FLIGHT_HOURS_MAX
    )
    diet = security_utils.sanitize_string(req.diet_type)
    electricity = security_utils.validate_numeric_input(
        req.electricity_kwh_per_year, 0, config.ELECTRICITY_KWH_MAX
    )
    waste = security_utils.validate_numeric_input(
        req.waste_kg_per_year, 0, config.WASTE_KG_MAX
    )
    
    # Run math
    emissions = calc_engine.calculate_personal_footprint(
        car_km, flights, diet, electricity, waste
    )
    equivalency = calc_engine.get_relatable_equivalencies(emissions["total_kg"])
    
    logger.info(
        f"calculate_personal endpoint success: total_kg={emissions['total_kg']}"
    )
    return {
        "status": "success",
        "data": {
            "emissions": emissions,
            "equivalency": equivalency
        }
    }

@app.post("/api/calculate/greensec")
async def calculate_greensec(req: GreenSecCalcRequest) -> Dict[str, Any]:
    """Calculates GreenSec carbon footprint from request data asynchronously.

    Addresses the root challenge of invisible compute waste by providing
    real-time carbon footprint evaluations of cryptographic operations,
    SIEM logging retention policies, vulnerability scans, and security VM
    host configurations, empowering security architects to align their
    decisions with green IT compliance.

    Args:
        req: GreenSec IT infrastructure parameters.

    Returns:
        A dictionary containing the detailed breakdown, savings, and equivalencies.
    """
    logger.info(
        f"calculate_greensec endpoint called with crypto_type={req.crypto_type}"
    )
    # Sanitize and validate inputs
    crypto_ops = security_utils.validate_numeric_input(
        req.crypto_ops_millions, 0, config.CRYPTO_OPS_MAX
    )
    crypto_type = security_utils.sanitize_string(req.crypto_type)
    log_size = security_utils.validate_numeric_input(
        req.log_size_gb, 0, config.LOG_SIZE_MAX
    )
    log_storage = security_utils.sanitize_string(req.log_storage_type)
    scan_runs = security_utils.validate_numeric_input(
        req.scan_runs_per_month, 0, config.SCAN_RUNS_MAX
    )
    scan_type = security_utils.sanitize_string(req.scan_type)
    server_hours = security_utils.validate_numeric_input(
        req.server_hours_per_month, 0, config.SERVER_HOURS_MAX
    )
    agent_type = security_utils.sanitize_string(req.agent_type)
    
    # Run math
    emissions = calc_engine.calculate_greensec_footprint(
        crypto_ops,
        crypto_type,
        log_size,
        log_storage,
        scan_runs,
        scan_type,
        server_hours,
        agent_type
    )
    equivalency = calc_engine.get_relatable_equivalencies(emissions["total_kg"])
    
    logger.info(
        f"calculate_greensec endpoint success: total_kg={emissions['total_kg']}"
    )
    return {
        "status": "success",
        "data": {
            "emissions": emissions,
            "equivalency": equivalency
        }
    }

@app.post("/api/state/sign")
async def sign_state(req: StateSignRequest) -> Dict[str, str]:
    """Encrypts and signs client-side database logs asynchronously.

    Ensures client-side calculation audits are cryptographically signed to prevent
    unauthorized tampering, guaranteeing that carbon ledger metrics remain secure
    and verifiable for enterprise reporting.

    Args:
        req: The state dictionary object to sign.

    Returns:
        A dictionary containing the payload and signature hash.
    """
    logger.info("sign_state endpoint called")
    secured = security_utils.encrypt_and_sign_state(req.state)
    if "error" in secured:
        logger.error(f"sign_state endpoint failed: {secured['message']}")
        raise HTTPException(status_code=500, detail=secured["message"])
    logger.info("sign_state endpoint success")
    return {
        "status": "secured",
        "payload": secured["payload"],
        "signature": secured["signature"]
    }

@app.post("/api/state/verify")
async def verify_state(req: StateVerifyRequest) -> Dict[str, Any]:
    """Verifies HMAC signature and decrypts database state asynchronously.

    Verifies the integrity of audit reports by validating the cryptographic
    signature, ensuring that user metrics have not been modified or compromised
    during client-side storage retrieval.

    Args:
        req: The payload and signature integrity values to check.

    Returns:
        The decryption verification status and verified state details.
    """
    logger.info("verify_state endpoint called")
    success, data = security_utils.decrypt_and_verify_state(
        req.payload, req.signature
    )
    if not success:
        logger.warning("verify_state endpoint integrity signature check failed")
        return {
            "status": "compromised",
            "error": data.get("error", "Verification failed"),
            "message": data.get("message", "The integrity signature does not match.")
        }
    logger.info("verify_state endpoint success")
    return {
        "status": "verified",
        "state": data
    }

@app.get("/api/leaderboard")
async def get_leaderboard() -> List[Dict[str, Any]]:
    """Serves simulated carbon audit leaderboard for IT teams.

    Returns:
        A list of ranking dictionaries.
    """
    return [
        {
            "rank": 1,
            "team": "Kernel Security Core",
            "score": 98.4,
            "mode": "GreenSec",
            "co2_saved_kg": 4820.0
        },
        {
            "rank": 2,
            "team": "Design & UI/UX Guild",
            "score": 94.2,
            "mode": "Personal",
            "co2_saved_kg": 2900.5
        },
        {
            "rank": 3,
            "team": "SecOps Automation",
            "score": 91.0,
            "mode": "GreenSec",
            "co2_saved_kg": 4150.2
        },
        {
            "rank": 4,
            "team": "API Integration Devs",
            "score": 86.5,
            "mode": "GreenSec",
            "co2_saved_kg": 1820.8
        },
        {
            "rank": 5,
            "team": "Product Growth Team",
            "score": 79.1,
            "mode": "Personal",
            "co2_saved_kg": 1200.0
        }
    ]

def _test_boundary_validation() -> Dict[str, Any]:
    try:
        assert security_utils.validate_numeric_input(-5.5) == 0.0
        assert security_utils.validate_numeric_input(100.0) == 100.0
        assert security_utils.validate_numeric_input("corrupt_string") == 0.0
        return {
            "name": "Backend Boundary Validation",
            "passed": True,
            "details": "Numeric filters clamping invalid inputs."
        }
    except Exception as e:
        return {
            "name": "Backend Boundary Validation",
            "passed": False,
            "details": str(e)
        }


def _test_xss_sanitization() -> Dict[str, Any]:
    try:
        payload = "<script>alert('xss')</script>"
        sanitized = security_utils.sanitize_string(payload)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
        return {
            "name": "XSS Input Sanitization",
            "passed": True,
            "details": f"Escaped HTML payload: {sanitized}"
        }
    except Exception as e:
        return {
            "name": "XSS Input Sanitization",
            "passed": False,
            "details": str(e)
        }


def _test_hmac_tamper_proofing() -> Dict[str, Any]:
    try:
        state_dict = {"score": 100, "user": "CISO"}
        signed = security_utils.encrypt_and_sign_state(state_dict)
        ok, verified = security_utils.decrypt_and_verify_state(
            signed["payload"], signed["signature"]
        )
        assert ok is True
        assert verified["score"] == 100
        
        # Test Tamper
        tampered_payload = signed["payload"] + "tamper"
        ok_tampered, _ = security_utils.decrypt_and_verify_state(
            tampered_payload, signed["signature"]
        )
        assert ok_tampered is False
        return {
            "name": "HMAC-SHA256 Cryptographic Tamper-Proofing",
            "passed": True,
            "details": "Tampering successfully detected and rejected."
        }
    except Exception as e:
        return {
            "name": "HMAC-SHA256 Cryptographic Tamper-Proofing",
            "passed": False,
            "details": str(e)
        }


def _test_personal_calc_math() -> Dict[str, Any]:
    try:
        res = calc_engine.calculate_personal_footprint(
            1000, 0, "vegetarian", 0, 0
        )
        assert res["components"]["car_co2"] == 180.0
        return {
            "name": "Personal Carbon Calculator Math",
            "passed": True,
            "details": "Core vehicle math matches references."
        }
    except Exception as e:
        return {
            "name": "Personal Carbon Calculator Math",
            "passed": False,
            "details": str(e)
        }


def _test_greensec_crypto_comparison() -> Dict[str, Any]:
    try:
        res_rsa = calc_engine.calculate_greensec_footprint(
            100, 
            "rsa4096", 
            0, 
            "cold_archive", 
            0, 
            "targeted_sast", 
            0, 
            "light_kernel"
        )
        res_ecc = calc_engine.calculate_greensec_footprint(
            100, 
            "ecc256", 
            0, 
            "cold_archive", 
            0, 
            "targeted_sast", 
            0, 
            "light_kernel"
        )
        assert res_rsa["total_kg"] > res_ecc["total_kg"]
        return {
            "name": "GreenSec Cryptographic Algorithm Comparison Math",
            "passed": True,
            "details": "RSA-4096 is energy-heavier than ECC-256."
        }
    except Exception as e:
        return {
            "name": "GreenSec Cryptographic Algorithm Comparison Math",
            "passed": False,
            "details": str(e)
        }


def _test_negative_clamping() -> Dict[str, Any]:
    try:
        assert security_utils.validate_numeric_input(-125.7, 0.0, 100000.0) == 0.0
        return {
            "name": "Negative Clamping Edge Case",
            "passed": True,
            "details": "Negative floats clamped to exactly 0.0."
        }
    except Exception as e:
        return {
            "name": "Negative Clamping Edge Case",
            "passed": False,
            "details": str(e)
        }


def _test_overflow_prevention() -> Dict[str, Any]:
    try:
        assert security_utils.validate_numeric_input(999999999.0, 0.0, 1000.0) == 1000.0
        return {
            "name": "High Value Overflow Prevention Edge Case",
            "passed": True,
            "details": "Overflow values clamped to upper boundary."
        }
    except Exception as e:
        return {
            "name": "High Value Overflow Prevention Edge Case",
            "passed": False,
            "details": str(e)
        }


@app.get("/api/tests")
async def execute_test_suite() -> Dict[str, Any]:
    """Triggers backend functional and validation checks for the Dev panel.

    Runs comprehensive regression tests for calculation math, validation
    boundaries, input sanitization, and cryptographic state signing to ensure the
    platform behaves reliably for audits.
    """
    test_results = [
        _test_boundary_validation(),
        _test_xss_sanitization(),
        _test_hmac_tamper_proofing(),
        _test_personal_calc_math(),
        _test_greensec_crypto_comparison(),
        _test_negative_clamping(),
        _test_overflow_prevention()
    ]
    overall = "PASSED" if all(t["passed"] for t in test_results) else "FAILED"
    return {
        "overall": overall,
        "tests": test_results
    }

# Ensure static folder exists
os.makedirs("static", exist_ok=True)

# Mount frontend Static Files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

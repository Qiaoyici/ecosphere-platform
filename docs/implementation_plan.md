# Enterprise Modularity & Linter Clean Sweep Plan

A rigorous sweep to resolve formatting issues, reduce cyclomatic complexity, and modularize code across Python and JavaScript layers to maximize Code Quality score.

## User Review Required

> [!WARNING]
> We will split the `execute_test_suite` endpoint logic into separate private helper functions (e.g. `_run_boundary_test()`, `_run_xss_test()`, etc.) to reduce cyclomatic complexity and long-function count in `main.py`.

> [!NOTE]
> All python code lines will be strictly reformatted to adhere to a maximum limit of **88 characters** (matching the standard Black formatter standard).

## Open Questions

None. The user requirements are clear and complete.

## Proposed Changes

---

### Backend Components

#### [MODIFY] [calc_engine.py](../calc_engine.py)
- Reformat all code to strictly ensure no line exceeds 88 characters.
- Modularize `calculate_personal_footprint` by moving math blocks into private helper functions:
  - `_calculate_car_co2()`
  - `_calculate_flight_co2()`
  - `_calculate_diet_co2()`
  - `_calculate_energy_co2()`
  - `_calculate_waste_co2()`
- Modularize `calculate_greensec_footprint` into:
  - `_calculate_crypto_co2()`
  - `_calculate_storage_co2()`
  - `_calculate_scan_co2()`
  - `_calculate_agent_co2()`
  - `_calculate_optimized_greensec_total()`

#### [MODIFY] [main.py](../main.py)
- Reformat code lines to strictly remain below 88 characters.
- Break down the long `execute_test_suite()` endpoint (over 70 lines) into private test-suite helpers:
  - `_test_boundary_validation()`
  - `_test_xss_sanitization()`
  - `_test_hmac_tamper_proofing()`
  - `_test_personal_calc_math()`
  - `_test_greensec_crypto_comparison()`
  - `_test_negative_clamping()`
  - `_test_overflow_prevention()`

#### [MODIFY] [security_utils.py](../security_utils.py)
- Break lines exceeding 88 characters into multiple lines (e.g., SECRET_KEY definition, hmac.new signature calls, validate_numeric_input signature).

---

### Frontend Components

#### [MODIFY] [app.js](../static/app.js)
- Ensure all functions conform to strict spacing and standard semicolons.
- Eliminate nested if/else statements by applying early returns (e.g. in warning nudge event handlers, visibility change logic, form handlers).

## Verification Plan

## Automated Tests
- Run `pytest` if a suite is present, and execute the backend automated test runner `/api/tests` to confirm no regressions were introduced.

## Manual Verification
- Launch the browser and run calculations in both modes to verify visual and state logic behavior remain fully functional.

# EcoSphere — Enterprise Carbon & GreenSec Risk Platform

> **Challenge 3: Carbon Footprint Awareness Platform**
> Design a solution that helps individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.

---

## Chosen Vertical

**Challenge 3 — Carbon Footprint Awareness Platform**

EcoSphere addresses carbon awareness from two angles most tools ignore together:
- **Personal lifestyle** (transport, diet, energy, waste)
- **Digital security infrastructure** (GreenSec) — the hidden carbon cost of cryptographic operations, SIEM logging, vulnerability scans, and host agents

---

## Approach and Logic

### Architecture
- **Backend:** FastAPI (Python) — `main.py` orchestrates endpoints, `calc_engine.py` handles all emission math, `security_utils.py` handles input sanitisation, HMAC signing, and tamper detection
- **Frontend:** Vanilla JS/HTML/CSS served as static files from `/static`
- **No database required** — all calculations are stateless and pure functions, cached with `lru_cache` for efficiency

### Emission Calculation Logic

**Personal footprint** (`/api/calculate/personal`) computes annual kg CO2 from:
| Input | Factor | Source |
|---|---|---|
| Car km/year | 0.18 kg CO2/km | IPCC AR6 |
| Flight hours/year | 90 kg CO2/hr | ICAO average |
| Diet type (8 options) | 1.3–7.2 kg CO2/day | Project Drawdown |
| Electricity kWh/year | 0.82 kg CO2/kWh | CEA India 2023 |
| Waste kg/year | 0.5 kg CO2/kg | IPCC landfill factors |

**GreenSec footprint** (`/api/calculate/greensec`) computes annual kg CO2 from IT security choices:
| Input | Example savings |
|---|---|
| Crypto algorithm | ECC-256 uses 16× less energy than RSA-4096 |
| Log storage type | Cold archive uses 7.5× less CO2 than hot storage |
| Scan type | Targeted SAST uses 25× less energy than full DAST |
| Agent type | eBPF kernel sensor uses 6× less energy than heavy agent |

### Personalised Insights
Results are translated into relatable equivalencies:
- Trees needed to offset the footprint
- Equivalent Delhi–Mumbai flights
- Smartphone charges
- Household electricity months
- **Actionable Recommendations**: Dynamic generation of 3 ranked, personalized footprint-reduction suggestions with exact calculated carbon savings and HSL-styled difficulty badges (`EASY`, `MODERATE`, `CHALLENGING`) customized to the user's highest emission categories.

### State Integrity
User session state is HMAC-SHA256 signed and Base64 encoded via `/api/state/sign` and `/api/state/verify`, enabling tamper detection without a database.

---

## How the Solution Works

1. User opens the web UI and selects either **Personal** or **GreenSec** mode
2. They fill in their lifestyle or IT infrastructure parameters
3. The frontend POSTs to the relevant `/api/calculate/` endpoint
4. The backend calculates emissions per category, totals them, and returns a category breakdown with relatable equivalencies
5. The backend also generates 3 ranked, personalized footprint-reduction recommendations based on the user's highest-emission categories, each with calculated CO2 savings and a difficulty rating
6. The leaderboard (`/api/leaderboard`) shows team-level rankings to encourage healthy competition
7. The dev panel (`/api/tests`) runs a built-in functional test suite to validate core logic

## Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/Qiaoyici/ecosphere-platform.git
cd ecosphere-platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set the required secret (never skip this)
export ECOSPHERE_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 4. Start the server
uvicorn main:app --reload --port 8000

# 5. Open http://localhost:8000
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/calculate/personal` | Personal carbon footprint |
| POST | `/api/calculate/greensec` | IT security carbon footprint |
| POST | `/api/state/sign` | HMAC-sign client state |
| POST | `/api/state/verify` | Verify and decrypt signed state |
| GET | `/api/leaderboard` | Team carbon audit rankings |
| GET | `/api/tests` | Run backend functional test suite |

---

## Assumptions Made

- Indian electricity grid intensity (0.82 kg CO2/kWh, CEA 2023) is used as the default since the platform is India-localised
- Diet emission factors are annual averages from Project Drawdown and do not account for regional food sourcing variation
- Flight emissions use a per-hour passenger share average and do not model radiative forcing multipliers
- GreenSec emission factors are derived from published cloud energy benchmarks and academic cryptography energy studies; exact values vary by hardware
- The leaderboard is seeded with representative sample data for demonstration purposes
- `ECOSPHERE_SECRET` must be set as an environment variable before startup; the server will refuse to start without it

---

## Evaluation Criteria Coverage

| Criterion | Implementation |
|---|---|
| **Code Quality** | Separated concerns across 3 modules; typed with Pydantic v2; full docstrings |
| **Security** | HMAC-SHA256 state signing; XSS sanitisation; input clamping; no hardcoded secrets |
| **Efficiency** | `lru_cache` on pure calculation functions; GZip middleware; async endpoints |
| **Testing** | `/api/tests` endpoint validates 9 functional cases including edge cases, tamper detection, and recommendation engine logic |
| **Accessibility** | Static frontend served directly; no login required; works on mobile browsers |

---

## Verification Evidence

Comprehensive implementation plans, task tracking lists, visual snapshots, and walkthrough recordings demonstrating the application's layout and test status are preserved in the [docs/](docs/) folder.


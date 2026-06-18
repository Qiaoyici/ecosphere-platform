"use strict";
// EcoSphere Application JavaScript
document.addEventListener("DOMContentLoaded", () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    // Debounce Utility (300ms delay by default)
    function debounce(func, delay = 300) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
            }, delay);
        };
    }

    // Application State
    const AppState = {
        activeMode: "personal", // "personal" or "greensec"
        personalEmissions: 0,
        greensecEmissions: 0,
        currentYearlyTotal: 0,
        personalInputs: {
            carKm: 8000,
            flightHours: 12,
            dietType: "low_meat",
            electricityKwh: 2400,
            wasteKg: 400
        },
        greensecInputs: {
            cryptoOps: 5000,
            cryptoType: "rsa4096",
            logSize: 1200,
            logStorage: "hot_storage",
            scanRuns: 25,
            scanType: "full_dast",
            serverHours: 1488,
            agentType: "heavy_agent"
        }
    };
    const state = AppState;

    // DOM Selectors
    const modeToggle = document.getElementById("modeToggle");
    const body = document.body;
    const personalForm = document.getElementById("personalForm");
    const greensecForm = document.getElementById("greensecForm");
    const personalNudgeBox = document.getElementById("personalNudgeBox");
    const greensecNudgeBox = document.getElementById("greensecNudgeBox");
    
    // Impact Equivalencies elements
    const treesVal = document.getElementById("treesVal");
    const chargesVal = document.getElementById("chargesVal");
    const flightsVal = document.getElementById("flightsVal");
    const electricityVal = document.getElementById("electricityVal");
    const overlayTotal = document.getElementById("overlayTotal");
    const sphereStatus = document.getElementById("sphereStatus");

    // Dev Modal elements
    const devConsoleToggle = document.getElementById("devConsoleToggle");
    const devModal = document.getElementById("devModal");
    const closeDevModal = document.getElementById("closeDevModal");
    const runTestsBtn = document.getElementById("runTestsBtn");
    const testProgress = document.getElementById("testProgress");
    const testResults = document.getElementById("testResults");
    const testSummaryStatus = document.getElementById("testSummaryStatus");
    const testList = document.getElementById("testList");

    // Canvas setup
    const canvas = document.getElementById("sphereCanvas");
    const ctx = canvas ? canvas.getContext("2d") : null;
    let animationFrameId;

    // ----------------- STATE SECURE STORAGE -----------------

    async function saveStateSecurely() {
        try {
            const response = await fetch("/api/state/sign", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ state: state })
            });
            const result = await response.json();
            if (result.status === "secured") {
                localStorage.setItem("ecosphere_payload", result.payload);
                localStorage.setItem("ecosphere_sig", result.signature);
            }
        } catch (e) {
            console.error("State securing failed:", e);
        }
    }

    async function loadStateSecurely() {
        const payload = localStorage.getItem("ecosphere_payload");
        const signature = localStorage.getItem("ecosphere_sig");
        
        if (!payload || !signature) {
            triggerCalculation();
            return;
        }

        try {
            const response = await fetch("/api/state/verify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ payload, signature })
            });
            const result = await response.json();
            if (result.status !== "verified") {
                console.warn("State verification failed (tampered). Restoring defaults.");
                triggerCalculation();
                return;
            }

            Object.assign(AppState, result.state);
            restoreFormInputs();
            if (modeToggle) {
                modeToggle.checked = (state.activeMode === "greensec");
                modeToggle.setAttribute("aria-checked", modeToggle.checked ? "true" : "false");
            }
            updateUIPalette();
        } catch (e) {
            console.error("State loading error:", e);
        }
        triggerCalculation();
    }

    function restoreFormInputs() {
        const carKm = document.getElementById("carKm");
        const flightHours = document.getElementById("flightHours");
        const dietType = document.getElementById("dietType");
        const electricityKwh = document.getElementById("electricityKwh");
        const wasteKg = document.getElementById("wasteKg");

        if (carKm) { carKm.value = state.personalInputs.carKm; }
        if (flightHours) { flightHours.value = state.personalInputs.flightHours; }
        if (dietType) { dietType.value = state.personalInputs.dietType; }
        if (electricityKwh) { electricityKwh.value = state.personalInputs.electricityKwh; }
        if (wasteKg) { wasteKg.value = state.personalInputs.wasteKg; }

        const cryptoOps = document.getElementById("cryptoOps");
        const cryptoType = document.getElementById("cryptoType");
        const logSize = document.getElementById("logSize");
        const logStorage = document.getElementById("logStorage");
        const scanRuns = document.getElementById("scanRuns");
        const scanType = document.getElementById("scanType");
        const serverHours = document.getElementById("serverHours");
        const agentType = document.getElementById("agentType");

        if (cryptoOps) { cryptoOps.value = state.greensecInputs.cryptoOps; }
        if (cryptoType) { cryptoType.value = state.greensecInputs.cryptoType; }
        if (logSize) { logSize.value = state.greensecInputs.logSize; }
        if (logStorage) { logStorage.value = state.greensecInputs.logStorage; }
        if (scanRuns) { scanRuns.value = state.greensecInputs.scanRuns; }
        if (scanType) { scanType.value = state.greensecInputs.scanType; }
        if (serverHours) { serverHours.value = state.greensecInputs.serverHours; }
        if (agentType) { agentType.value = state.greensecInputs.agentType; }
    }

    // ----------------- REST API CALCULATIONS -----------------

    async function triggerPersonalCalculation() {
        const carKmEl = document.getElementById("carKm");
        const flightHoursEl = document.getElementById("flightHours");
        const dietTypeEl = document.getElementById("dietType");
        const electricityKwhEl = document.getElementById("electricityKwh");
        const wasteKgEl = document.getElementById("wasteKg");

        if (!carKmEl || !flightHoursEl || !dietTypeEl || !electricityKwhEl || !wasteKgEl) {
            return;
        }

        const payload = {
            car_km_per_year: parseFloat(carKmEl.value),
            flight_hours_per_year: parseFloat(flightHoursEl.value),
            diet_type: dietTypeEl.value,
            electricity_kwh_per_year: parseFloat(electricityKwhEl.value),
            waste_kg_per_year: parseFloat(wasteKgEl.value)
        };
        
        state.personalInputs = {
            carKm: payload.car_km_per_year,
            flightHours: payload.flight_hours_per_year,
            dietType: payload.diet_type,
            electricityKwh: payload.electricity_kwh_per_year,
            wasteKg: payload.waste_kg_per_year
        };

        try {
            const response = await fetch("/api/calculate/personal", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            if (result.status === "success") {
                state.personalEmissions = result.data.emissions.total_kg;
                state.currentYearlyTotal = state.personalEmissions;
                updateUIResults(result.data);
            }
        } catch (e) {
            console.error("Personal footprint calculation failed:", e);
        }
    }

    async function triggerGreensecCalculation() {
        const cryptoOpsEl = document.getElementById("cryptoOps");
        const cryptoTypeEl = document.getElementById("cryptoType");
        const logSizeEl = document.getElementById("logSize");
        const logStorageEl = document.getElementById("logStorage");
        const scanRunsEl = document.getElementById("scanRuns");
        const scanTypeEl = document.getElementById("scanType");
        const serverHoursEl = document.getElementById("serverHours");
        const agentTypeEl = document.getElementById("agentType");

        if (!cryptoOpsEl || !cryptoTypeEl || !logSizeEl || !logStorageEl || !scanRunsEl || !scanTypeEl || !serverHoursEl || !agentTypeEl) {
            return;
        }

        const payload = {
            crypto_ops_millions: parseFloat(cryptoOpsEl.value),
            crypto_type: cryptoTypeEl.value,
            log_size_gb: parseFloat(logSizeEl.value),
            log_storage_type: logStorageEl.value,
            scan_runs_per_month: parseFloat(scanRunsEl.value),
            scan_type: scanTypeEl.value,
            server_hours_per_month: parseFloat(serverHoursEl.value),
            agent_type: agentTypeEl.value
        };

        state.greensecInputs = {
            cryptoOps: payload.crypto_ops_millions,
            cryptoType: payload.crypto_type,
            logSize: payload.log_size_gb,
            logStorage: payload.log_storage_type,
            scanRuns: payload.scan_runs_per_month,
            scanType: payload.scan_type,
            serverHours: payload.server_hours_per_month,
            agentType: payload.agent_type
        };

        try {
            const response = await fetch("/api/calculate/greensec", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            if (result.status === "success") {
                state.greensecEmissions = result.data.emissions.total_kg;
                state.currentYearlyTotal = state.greensecEmissions;
                updateUIResults(result.data);
            }
        } catch (e) {
            console.error("GreenSec calculation failed:", e);
        }
    }

    async function triggerCalculation() {
        if (state.activeMode === "personal") {
            await triggerPersonalCalculation();
        } else {
            await triggerGreensecCalculation();
        }
        await saveStateSecurely();
    }

    const debouncedTriggerCalculation = debounce(triggerCalculation, 300);

    function updatePersonalStatusText(total) {
        if (total < 2500) {
            sphereStatus.innerText = "🍃 Ecosystem Health: Excellent";
            sphereStatus.style.color = "#00ff66";
            return;
        }
        if (total < 6000) {
            sphereStatus.innerText = "⚠️ Ecosystem Health: Moderate Strain";
            sphereStatus.style.color = "#ffb74d";
            return;
        }
        sphereStatus.innerText = "🚨 Ecosystem Health: Critical Risk";
        sphereStatus.style.color = "#ff4d4d";
    }

    function updateGreensecStatusText(total) {
        if (total < 1000) {
            sphereStatus.innerText = "💻 GreenSec Posture: Optimal (Lightweight)";
            sphereStatus.style.color = "#00ff66";
            return;
        }
        if (total < 4000) {
            sphereStatus.innerText = "⚠️ GreenSec Posture: Warning (High-CPU overhead)";
            sphereStatus.style.color = "#ffb74d";
            return;
        }
        sphereStatus.innerText = "🚨 GreenSec Posture: Warning (Severe digital waste)";
        sphereStatus.style.color = "#ff4d4d";
    }

    function updateSphereStatusText(total) {
        if (!sphereStatus) {
            return;
        }
        if (state.activeMode === "personal") {
            updatePersonalStatusText(total);
            return;
        }
        updateGreensecStatusText(total);
    }

    function updateUIResults(data) {
        if (!data || !data.emissions) {
            return;
        }
        if (overlayTotal) {
            overlayTotal.innerText = data.emissions.total_kg.toLocaleString(undefined, {
                minimumFractionDigits: 1,
                maximumFractionDigits: 1
            });
        }
        
        updateSphereStatusText(data.emissions.total_kg);

        if (treesVal) {
            treesVal.innerText = data.equivalency.trees_planted.toLocaleString(undefined, {
                maximumFractionDigits: 1
            });
        }
        if (chargesVal) {
            chargesVal.innerText = data.equivalency.smartphone_charges.toLocaleString(undefined, {
                maximumFractionDigits: 0
            });
        }
        if (flightsVal) {
            flightsVal.innerText = data.equivalency.delhi_mumbai_flights.toLocaleString(undefined, {
                maximumFractionDigits: 1
            });
        }
        if (electricityVal) {
            electricityVal.innerText = data.equivalency.household_electricity_months.toLocaleString(undefined, {
                maximumFractionDigits: 1
            });
        }
    }

    // ----------------- LEADERBOARD LOADER -----------------

    async function loadLeaderboard() {
        const leaderboardBody = document.getElementById("leaderboardBody");
        if (!leaderboardBody) {
            return;
        }
        try {
            const response = await fetch("/api/leaderboard");
            const result = await response.json();
            leaderboardBody.innerHTML = "";
            
            const fragment = document.createDocumentFragment();
            result.forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>#${row.rank}</strong></td>
                    <td>${row.team} <span class="badge ${row.mode === "GreenSec" ? "passed" : ""}" style="font-size: 8px; margin-left: 6px;">${row.mode}</span></td>
                    <td>${row.score}%</td>
                    <td class="green-text">+${row.co2_saved_kg.toLocaleString()} kg</td>
                `;
                fragment.appendChild(tr);
            });
            leaderboardBody.appendChild(fragment);
        } catch (e) {
            console.error("Leaderboard loading failed:", e);
        }
    }

    // ----------------- FORM SUBMIT LISTENERS -----------------

    if (personalForm) {
        personalForm.addEventListener("submit", (e) => {
            e.preventDefault();
            triggerCalculation();
        });
    }

    if (greensecForm) {
        greensecForm.addEventListener("submit", (e) => {
            e.preventDefault();
            triggerCalculation();
        });
    }

    // Attach debounced auto-calculation on input and change events
    const inputsToWatch = [
        "carKm", "flightHours", "dietType", "electricityKwh", "wasteKg",
        "cryptoOps", "cryptoType", "logSize", "logStorage", "scanRuns", "scanType", "serverHours", "agentType"
    ];

    inputsToWatch.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", debouncedTriggerCalculation);
            el.addEventListener("change", debouncedTriggerCalculation);
        }
    });

    // ----------------- NUDGE SELECTORS -----------------

    function handlePersonalNudgeClick(btn) {
        document.querySelectorAll("#personalNudgeBox .nudge-choice-btn").forEach(b => {
            b.classList.remove("active");
            b.setAttribute("aria-pressed", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-pressed", "true");
        const type = btn.getAttribute("data-type");
        const resultBox = document.getElementById("personalNudgeResult");
        if (!resultBox) {
            return;
        }

        if (type === "beef") {
            resultBox.className = "nudge-alert warning";
            resultBox.innerHTML = `
                <i data-lucide="info" class="nudge-icon" aria-hidden="true"></i>
                <div class="nudge-content">
                    <strong>Carbon Alert:</strong> Choosing the Beef Burger creates <strong>5.8 kg CO₂e</strong>. Consuming this daily uses the equivalent carbon of running RSA-4096 cryptography all year!
                </div>
            `;
            lucide.createIcons();
            return;
        }

        resultBox.className = "nudge-alert info";
        resultBox.innerHTML = `
            <i data-lucide="leaf" class="nudge-icon" aria-hidden="true"></i>
            <div class="nudge-content">
                <strong>Eco-optimized Choice:</strong> Grilled Tofu & Lentil Salad generates only <strong>0.9 kg CO₂e</strong>. By making this choice, you save <strong>4.9 kg CO₂e</strong> immediately!
            </div>
        `;
        lucide.createIcons();
    }

    document.querySelectorAll("#personalNudgeBox .nudge-choice-btn").forEach(btn => {
        btn.addEventListener("click", () => handlePersonalNudgeClick(btn));
    });

    function handleDietTypeChange() {
        const dietTypeSelect = document.getElementById("dietType");
        if (!dietTypeSelect) {
            return;
        }
        const val = dietTypeSelect.value;
        const resultBox = document.getElementById("personalNudgeResult");
        if (!resultBox) {
            return;
        }

        if (val === "beef_heavy" || val === "high_meat") {
            resultBox.className = "nudge-alert warning";
            resultBox.innerHTML = `
                <i data-lucide="info" class="nudge-icon" aria-hidden="true"></i>
                <div class="nudge-content">
                    <strong>Carbon Alert (High Carbon Diet):</strong> Selecting a meat-heavy diet generates up to <strong>2.6 tons of CO₂e</strong> annually. Swap to <strong>Locally-sourced Organic Veg</strong> or <strong>Plant-based Alternatives</strong> to reduce your footprint by over 80%!
                </div>
            `;
            lucide.createIcons();
            return;
        }

        resultBox.className = "nudge-alert info";
        resultBox.innerHTML = `
            <i data-lucide="leaf" class="nudge-icon" aria-hidden="true"></i>
            <div class="nudge-content">
                <strong>Eco-optimized Choice:</strong> Lower meat and plant-based selections keep your annual dietary footprint under <strong>0.5 tons of CO₂e</strong>, saving equivalent emissions to planting dozens of mature trees.
            </div>
        `;
        lucide.createIcons();
    }

    const dietTypeSelect = document.getElementById("dietType");
    if (dietTypeSelect) {
        dietTypeSelect.addEventListener("change", handleDietTypeChange);
    }

    function handleCryptoTypeChange() {
        const cryptoTypeSelect = document.getElementById("cryptoType");
        if (!cryptoTypeSelect) {
            return;
        }
        const val = cryptoTypeSelect.value;
        const resultBox = document.getElementById("greensecNudgeResult");
        if (!resultBox) {
            return;
        }

        if (val === "rsa4096" || val === "rsa2048") {
            resultBox.className = "nudge-alert warning";
            resultBox.innerHTML = `
                <i data-lucide="terminal" class="nudge-icon" aria-hidden="true"></i>
                <div class="nudge-content">
                    <strong>Carbon Alert (RSA Key Cryptography):</strong> Deploying RSA handshakes consumes up to <strong>16x more CPU energy</strong> than ECC algorithms under load. Swap to <strong>ECC-256 / Ed25519</strong> to save up to <strong>2.4 tons of CO₂e</strong> annually!
                </div>
            `;
            lucide.createIcons();
            return;
        }

        resultBox.className = "nudge-alert info";
        resultBox.innerHTML = `
            <i data-lucide="shield-check" class="nudge-icon" aria-hidden="true"></i>
            <div class="nudge-content">
                <strong>Security & Carbon Optimized:</strong> ECC-256 uses short keys, yielding <strong>90% lower CPU utilization</strong> while offering identical cryptographic strength. GreenSec optimal choice.
            </div>
        `;
        lucide.createIcons();
    }

    const cryptoTypeSelect = document.getElementById("cryptoType");
    if (cryptoTypeSelect) {
        cryptoTypeSelect.addEventListener("change", handleCryptoTypeChange);
    }

    function handleGreensecNudgeClick(btn) {
        document.querySelectorAll("#greensecNudgeBox .nudge-choice-btn").forEach(b => {
            b.classList.remove("active");
            b.setAttribute("aria-pressed", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-pressed", "true");
        const type = btn.getAttribute("data-type");
        const resultBox = document.getElementById("greensecNudgeResult");
        if (!resultBox) {
            return;
        }

        if (type === "rsa") {
            resultBox.className = "nudge-alert warning";
            resultBox.innerHTML = `
                <i data-lucide="terminal" class="nudge-icon" aria-hidden="true"></i>
                <div class="nudge-content">
                    <strong>System Warning:</strong> Under high production load, RSA-4096 handshake validations will consume <strong>16x</strong> more CPU cycles than ECC-256, adding <strong>2.4 tons of CO₂e</strong> annually. ed25519 recommended.
                </div>
            `;
            lucide.createIcons();
            return;
        }

        resultBox.className = "nudge-alert info";
        resultBox.innerHTML = `
            <i data-lucide="shield-check" class="nudge-icon" aria-hidden="true"></i>
            <div class="nudge-content">
                <strong>Security & Carbon Optimized:</strong> ECC-256 (elliptic curve) uses short keys, yielding <strong>90% lower CPU utilization</strong> while offering identical cryptographic strength. Fits GreenSec requirements.
            </div>
        `;
        lucide.createIcons();
    }

    document.querySelectorAll("#greensecNudgeBox .nudge-choice-btn").forEach(btn => {
        btn.addEventListener("click", () => handleGreensecNudgeClick(btn));
    });

    // ----------------- PALETTE SWAP & SWITCH TOGGLE -----------------

    if (modeToggle) {
        modeToggle.addEventListener("change", () => {
            state.activeMode = modeToggle.checked ? "greensec" : "personal";
            modeToggle.setAttribute("aria-checked", modeToggle.checked ? "true" : "false");
            updateUIPalette();
            triggerCalculation();
        });
    }

    function updateUIPalette() {
        if (!body || !personalForm || !greensecForm || !personalNudgeBox || !greensecNudgeBox) {
            return;
        }
        const logoIcon = document.querySelector(".logo-icon");
        if (state.activeMode === "personal") {
            body.className = "theme-personal";
            personalForm.classList.remove("hidden");
            greensecForm.classList.add("hidden");
            personalNudgeBox.classList.remove("hidden");
            greensecNudgeBox.classList.add("hidden");
            if (logoIcon) {
                logoIcon.setAttribute("class", "logo-icon green-glow");
            }
            lucide.createIcons();
            return;
        }

        body.className = "theme-greensec";
        personalForm.classList.add("hidden");
        greensecForm.classList.remove("hidden");
        personalNudgeBox.classList.add("hidden");
        greensecNudgeBox.classList.remove("hidden");
        if (logoIcon) {
            logoIcon.setAttribute("class", "logo-icon cyan-glow");
        }
        lucide.createIcons();
    }

    // ----------------- ECOSPHERE ANIMATED CANVAS -----------------

    // Floating particles state
    const particles = [];
    const particleCount = 20;
    if (canvas) {
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                speedX: (Math.random() - 0.5) * 0.8,
                speedY: (Math.random() - 0.5) * 0.8,
                radius: Math.random() * 2 + 1,
                color: 'rgba(255,255,255,0.3)'
            });
        }
    }

    let sunAngle = 0;

    function drawPersonalSphere(centerX, centerY, radius, severity) {
        const skyGrad = ctx.createLinearGradient(0, centerY - radius, 0, centerY + radius);
        const blueSkyColor = `hsl(200, 70%, ${70 - (severity * 30)}%)`;
        const dirtySkyColor = `hsl(28, ${15 + (severity * 10)}%, ${60 - (severity * 30)}%)`;
        skyGrad.addColorStop(0, blueSkyColor);
        skyGrad.addColorStop(1, dirtySkyColor);

        ctx.save();
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.clip();
        
        ctx.fillStyle = skyGrad;
        ctx.fillRect(centerX - radius, centerY - radius, radius * 2, radius * 2);

        sunAngle += 0.005;
        const sunX = centerX + Math.cos(sunAngle) * 70;
        const sunY = centerY - 50 + Math.sin(sunAngle) * 20;
        ctx.beginPath();
        ctx.arc(sunX, sunY, 15, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 235, 59, ${1 - severity})`;
        ctx.shadowBlur = 20;
        ctx.shadowColor = "#fffb7d";
        ctx.fill();
        ctx.shadowBlur = 0;

        if (severity > 0.1) {
            ctx.fillStyle = `rgba(100, 100, 100, ${severity * 0.4})`;
            for (let i = 0; i < severity * 30; i++) {
                ctx.beginPath();
                const smogX = (centerX - radius) + ((Math.sin(sunAngle + i) + 1) / 2) * (radius * 2);
                const smogY = (centerY - radius) + ((Math.cos(sunAngle * 0.5 + i) + 1) / 2) * (radius * 1.5);
                ctx.arc(smogX, smogY, Math.sin(sunAngle + i) * 6 + 10, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        ctx.beginPath();
        ctx.moveTo(centerX - radius, centerY + 60);
        ctx.quadraticCurveTo(centerX - 30, centerY + 20, centerX + 40, centerY + 50);
        ctx.quadraticCurveTo(centerX + 80, centerY + 30, centerX + radius, centerY + 70);
        ctx.lineTo(centerX + radius, centerY + radius);
        ctx.lineTo(centerX - radius, centerY + radius);
        ctx.closePath();
        
        const grassColor = `hsl(${120 - (severity * 90)}, ${40 - (severity * 15)}%, ${40 - (severity * 10)}%)`;
        ctx.fillStyle = grassColor;
        ctx.fill();

        const treeCount = Math.max(1, Math.round(8 * (1 - severity)));
        const trunkColor = "#5d4037";

        for (let i = 0; i < treeCount; i++) {
            const tx = centerX - 80 + i * 22;
            const ty = centerY + 45 + Math.sin(i * 4.5) * 5;
            
            ctx.fillStyle = trunkColor;
            ctx.fillRect(tx - 2, ty - 10, 4, 10);

            ctx.beginPath();
            ctx.arc(tx, ty - 14, 8, 0, Math.PI * 2);
            ctx.fillStyle = `hsl(${120 - (severity * 80)}, 50%, ${30 - (severity * 10)}%)`;
            ctx.fill();
        }

        if (severity > 0.8) {
            ctx.font = "bold 10px var(--font-sans)";
            ctx.fillStyle = "#ff4d4d";
            ctx.textAlign = "center";
            ctx.fillText("ECOSYSTEM CRITICAL", centerX, centerY + 90);
        }

        ctx.restore();
    }

    function drawGreensecSphere(centerX, centerY, radius, severity) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.clip();

        ctx.fillStyle = "#03060d";
        ctx.fillRect(centerX - radius, centerY - radius, radius * 2, radius * 2);

        ctx.strokeStyle = `rgba(0, 240, 255, ${0.05 + (severity * 0.05)})`;
        ctx.lineWidth = 1;
        
        for (let y = centerY - radius; y < centerY + radius; y += 15) {
            ctx.beginPath();
            ctx.moveTo(centerX - radius, y);
            ctx.lineTo(centerX + radius, y);
            ctx.stroke();
        }
        for (let x = centerX - radius; x < centerX + radius; x += 15) {
            ctx.beginPath();
            ctx.moveTo(x, centerY - radius);
            ctx.lineTo(x, centerY + radius);
            ctx.stroke();
        }

        const rackCount = 3;
        const rackW = 30;
        const rackH = 70;
        
        for (let i = 0; i < rackCount; i++) {
            const rx = centerX - 60 + i * 48;
            const ry = centerY - 35;
            
            ctx.fillStyle = "#0c1527";
            ctx.strokeStyle = `rgba(0, 240, 255, ${0.4 - (severity * 0.2)})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.rect(rx, ry, rackW, rackH);
            ctx.fill();
            ctx.stroke();

            ctx.fillStyle = `rgba(0, 240, 255, ${0.1})`;
            for (let j = 0; j < 5; j++) {
                ctx.fillRect(rx + 3, ry + 4 + j * 12, rackW - 6, 8);
                
                ctx.beginPath();
                ctx.arc(rx + 8, ry + 8 + j * 12, 1.5, 0, Math.PI * 2);
                
                if (severity > 0.6) {
                    ctx.fillStyle = Math.random() > 0.4 ? "#ff4d4d" : "#ff9800";
                } else {
                    ctx.fillStyle = Math.random() > 0.2 ? "#00ff66" : "#00f0ff";
                }
                ctx.fill();
            }
        }

        if (severity > 0.2) {
            ctx.fillStyle = `rgba(255, 77, 77, ${severity * 0.5})`;
            for (let i = 0; i < severity * 15; i++) {
                ctx.beginPath();
                const sparkX = centerX - 60 + Math.random() * 120;
                const sparkY = centerY - 40 + Math.random() * 80;
                ctx.arc(sparkX, sparkY, Math.random() * 3 + 1, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        const fanAngle = sunAngle * (1 + severity * 8);
        ctx.strokeStyle = severity > 0.6 ? "#ff4d4d" : "#00f0ff";
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        ctx.arc(centerX, centerY + 65, 12, 0, Math.PI * 2);
        ctx.stroke();

        ctx.save();
        ctx.translate(centerX, centerY + 65);
        ctx.rotate(fanAngle);
        ctx.beginPath();
        ctx.moveTo(0, -9); ctx.lineTo(0, 9);
        ctx.moveTo(-9, 0); ctx.lineTo(9, 0);
        ctx.stroke();
        ctx.restore();

        ctx.font = "bold 9px var(--font-mono)";
        ctx.fillStyle = severity > 0.6 ? "#ff4d4d" : "#00ff66";
        ctx.textAlign = "center";
        ctx.fillText(severity > 0.6 ? "LOAD: OVERHEATED" : "SYS: ECO-OPTIMIZED", centerX, centerY - 55);

        ctx.restore();
    }

    function renderSphere() {
        if (document.hidden) {
            animationFrameId = null;
            return;
        }
        if (!canvas || !ctx) {
            return;
        }
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 110;

        const maxExpected = state.activeMode === "personal" ? 12000 : 6000;
        const severity = Math.min(1.0, state.currentYearlyTotal / maxExpected);

        if (state.activeMode === "personal") {
            drawPersonalSphere(centerX, centerY, radius, severity);
        } else {
            drawGreensecSphere(centerX, centerY, radius, severity);
        }

        ctx.strokeStyle = state.activeMode === "personal" ? "rgba(46, 125, 50, 0.4)" : "rgba(0, 240, 255, 0.4)";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.stroke();

        ctx.strokeStyle = state.activeMode === "personal" ? "rgba(46, 125, 50, 0.15)" : "rgba(0, 240, 255, 0.15)";
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius + 10, Math.PI * 0.1, Math.PI * 0.9);
        ctx.stroke();

        animationFrameId = requestAnimationFrame(renderSphere);
    }

    // Start Canvas Loop
    if (canvas && ctx) {
        renderSphere();
    }

    // Pause / resume canvas rendering on tab visibility changes
    document.addEventListener("visibilitychange", () => {
        if (!document.hidden && !animationFrameId && canvas && ctx) {
            renderSphere();
        }
    });

    // ----------------- DEVELOPER TEST SUITE CONSOLE -----------------

    function toggleDevModal() {
        if (!devModal || !devConsoleToggle) {
            return;
        }
        devModal.classList.toggle("hidden");
        const isHidden = devModal.classList.contains("hidden");
        devConsoleToggle.setAttribute("aria-expanded", !isHidden ? "true" : "false");
    }

    if (devConsoleToggle) {
        devConsoleToggle.addEventListener("click", toggleDevModal);
    }
    if (closeDevModal) {
        closeDevModal.addEventListener("click", toggleDevModal);
    }

    // Keyboard shortcut (Ctrl + Shift + D)
    window.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "d") {
            e.preventDefault();
            toggleDevModal();
        }
    });

    async function runAutomatedTests() {
        if (!runTestsBtn || !testProgress || !testResults || !testList || !testSummaryStatus) {
            return;
        }
        runTestsBtn.disabled = true;
        testProgress.classList.remove("hidden");
        testResults.classList.add("hidden");
        testList.innerHTML = "";

        try {
            const response = await fetch("/api/tests");
            const result = await response.json();
            
            testSummaryStatus.innerText = result.overall;
            testSummaryStatus.className = `badge ${result.overall === "PASSED" ? "passed" : "failed"}`;

            const fragment = document.createDocumentFragment();
            result.tests.forEach(test => {
                const item = document.createElement("div");
                item.className = "test-item";
                item.style.borderLeftColor = test.passed ? "#00ff66" : "#ff4d4d";
                item.innerHTML = `
                    <div class="test-item-header">
                        <span>${test.name}</span>
                        <span class="badge ${test.passed ? "passed" : "failed"}">${test.passed ? "PASSED" : "FAILED"}</span>
                    </div>
                    <div class="test-item-details">${test.details}</div>
                `;
                fragment.appendChild(item);
            });
            testList.appendChild(fragment);
            
            testResults.classList.remove("hidden");
        } catch (e) {
            console.error("Test execution failed:", e);
            testSummaryStatus.innerText = "ERROR";
            testSummaryStatus.className = "badge failed";
        } finally {
            testProgress.classList.add("hidden");
            runTestsBtn.disabled = false;
        }
    }

    if (runTestsBtn) {
        runTestsBtn.addEventListener("click", runAutomatedTests);
    }

    // Initialize Page
    loadStateSecurely();
    loadLeaderboard();
});

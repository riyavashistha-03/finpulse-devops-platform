/**
 * FinPulse Web Application Client Script
 * Handles live charts, market filters, portfolio CRUD, alerts engine, and auth flows.
 */

let marketChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    initChart();
    initFilters();
    initAuthForms();
    initPortfolio();
    initAlerts();
});

// --- CHART ENGINE ---
function initChart() {
    const canvas = document.getElementById("marketChart");
    if (!canvas) return;

    const select = document.getElementById("asset-chart-select");
    if (select) {
        select.addEventListener("change", (e) => loadChartForAsset(e.target.value));
        loadChartForAsset(select.value || "BTC");
    }
}

async function loadChartForAsset(symbol) {
    const canvas = document.getElementById("marketChart");
    if (!canvas) return;

    const select = document.getElementById("asset-chart-select");
    if (select && select.value !== symbol) {
        select.value = symbol;
    }

    try {
        const response = await fetch(`/api/market/history/${symbol}`);
        const result = await response.json();
        if (result.status === "success" && result.data) {
            renderChart(result.data);
        }
    } catch (err) {
        console.error("Failed to load asset chart history:", err);
    }
}

function renderChart(data) {
    const ctx = document.getElementById("marketChart").getContext("2d");
    const isPositive = data.change_24h >= 0;
    const lineColor = isPositive ? "#10b981" : "#ef4444";
    const bgGradient = ctx.createLinearGradient(0, 0, 0, 300);
    bgGradient.addColorStop(0, isPositive ? "rgba(16, 185, 129, 0.25)" : "rgba(239, 68, 68, 0.25)");
    bgGradient.addColorStop(1, "rgba(0, 0, 0, 0)");

    if (marketChartInstance) {
        marketChartInstance.destroy();
    }

    marketChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                label: `${data.symbol} Price (USD)`,
                data: data.points,
                borderColor: lineColor,
                backgroundColor: bgGradient,
                borderWidth: 2.5,
                fill: true,
                tension: 0.35,
                pointRadius: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `$${ctx.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#9ca3af" }
                },
                y: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: {
                        color: "#9ca3af",
                        callback: (v) => `$${v.toLocaleString()}`
                    }
                }
            }
        }
    });
}

// --- MARKET FILTER ---
function initFilters() {
    const buttons = document.querySelectorAll(".filter-btn");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const filter = btn.getAttribute("data-filter");
            const cards = document.querySelectorAll("#tickersGrid .ticker-card");
            cards.forEach(card => {
                if (filter === "all" || card.getAttribute("data-type") === filter) {
                    card.style.display = "flex";
                } else {
                    card.style.display = "none";
                }
            });
        });
    });
}

// --- PORTFOLIO ENGINE ---
function initPortfolio() {
    const tableBody = document.getElementById("portfolioTableBody");
    if (!tableBody) return;

    loadPortfolioData();

    const openBtn = document.getElementById("openAddAssetModal");
    const closeBtn = document.getElementById("closeAddAssetModal");
    const cancelBtn = document.getElementById("cancelAddAsset");
    const modal = document.getElementById("addAssetModal");
    const refreshBtn = document.getElementById("refreshPortfolioBtn");

    if (openBtn && modal) openBtn.addEventListener("click", () => modal.classList.add("active"));
    if (closeBtn && modal) closeBtn.addEventListener("click", () => modal.classList.remove("active"));
    if (cancelBtn && modal) cancelBtn.addEventListener("click", () => modal.classList.remove("active"));
    if (refreshBtn) refreshBtn.addEventListener("click", loadPortfolioData);

    const form = document.getElementById("addAssetForm");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const symbol = document.getElementById("asset_symbol").value;
            const quantity = parseFloat(document.getElementById("quantity").value);
            const buy_price = parseFloat(document.getElementById("buy_price").value);
            const notes = document.getElementById("notes").value;

            try {
                const res = await fetch("/api/portfolio", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ asset_symbol: symbol, quantity, buy_price, notes })
                });
                const data = await res.json();
                if (res.ok) {
                    modal.classList.remove("active");
                    form.reset();
                    loadPortfolioData();
                } else {
                    alert(data.message || "Failed to add asset");
                }
            } catch (err) {
                console.error("Error adding asset:", err);
            }
        });
    }
}

async function loadPortfolioData() {
    const tableBody = document.getElementById("portfolioTableBody");
    if (!tableBody) return;

    try {
        const res = await fetch("/api/portfolio");
        if (res.status === 401) {
            window.location.href = "/login";
            return;
        }
        const json = await res.json();
        const p = json.portfolio;

        // Update cards
        document.getElementById("totalNetValue").textContent = `$${p.total_current_value.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        document.getElementById("totalCostBasis").textContent = `$${p.total_invested.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        
        const pnlEl = document.getElementById("totalPnl");
        const pnlPctEl = document.getElementById("totalPnlPct");
        const isPos = p.total_pnl >= 0;
        
        pnlEl.textContent = `${isPos ? '+' : ''}$${p.total_pnl.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        pnlEl.className = `metric-value ${isPos ? 'text-success' : 'text-danger'}`;
        pnlPctEl.textContent = `${isPos ? '+' : ''}${p.total_pnl_percentage.toFixed(2)}%`;
        pnlPctEl.className = `metric-sub ${isPos ? 'text-success' : 'text-danger'}`;
        document.getElementById("totalHoldingsCount").textContent = p.total_items;

        if (p.items.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="10" class="text-center py-4 text-muted">No assets found in portfolio. Click 'Add Asset Holding' above to get started.</td></tr>`;
            return;
        }

        tableBody.innerHTML = p.items.map(item => {
            const pos = item.unrealized_pnl >= 0;
            return `
                <tr>
                    <td><strong>${item.asset_symbol}</strong> <span class="text-muted text-sm">(${item.asset_name})</span></td>
                    <td><span class="asset-badge ${item.asset_type}">${item.asset_type}</span></td>
                    <td>${item.quantity}</td>
                    <td>$${item.buy_price.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td><strong>$${item.current_price.toLocaleString(undefined, {minimumFractionDigits: 2})}</strong></td>
                    <td>$${item.total_cost.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td><strong>$${item.current_value.toLocaleString(undefined, {minimumFractionDigits: 2})}</strong></td>
                    <td class="${pos ? 'positive' : 'negative'}">
                        <strong>${pos ? '+' : ''}$${item.unrealized_pnl.toLocaleString(undefined, {minimumFractionDigits: 2})}</strong>
                        (${pos ? '+' : ''}${item.pnl_percentage.toFixed(2)}%)
                    </td>
                    <td class="text-muted text-sm">${item.notes || '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline text-danger" onclick="deletePortfolioAsset(${item.id})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
    } catch (err) {
        console.error("Error fetching portfolio:", err);
    }
}

async function deletePortfolioAsset(id) {
    if (!confirm("Are you sure you want to remove this asset holding?")) return;
    try {
        const res = await fetch(`/api/portfolio/${id}`, { method: "DELETE" });
        if (res.ok) loadPortfolioData();
    } catch (err) {
        console.error("Error deleting asset:", err);
    }
}

// --- ALERTS ENGINE ---
function initAlerts() {
    const tableBody = document.getElementById("alertsTableBody");
    if (!tableBody) return;

    loadAlertsData();

    const openBtn = document.getElementById("openAddAlertModal");
    const closeBtn = document.getElementById("closeAddAlertModal");
    const cancelBtn = document.getElementById("cancelAddAlert");
    const modal = document.getElementById("addAlertModal");
    const evalBtn = document.getElementById("evaluateAlertsBtn");

    if (openBtn && modal) openBtn.addEventListener("click", () => modal.classList.add("active"));
    if (closeBtn && modal) closeBtn.addEventListener("click", () => modal.classList.remove("active"));
    if (cancelBtn && modal) cancelBtn.addEventListener("click", () => modal.classList.remove("active"));
    
    if (evalBtn) {
        evalBtn.addEventListener("click", async () => {
            evalBtn.disabled = true;
            evalBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Evaluating...`;
            try {
                const res = await fetch("/api/alerts/evaluate", { method: "POST" });
                const json = await res.json();
                loadAlertsData();
                if (json.triggered_count > 0) {
                    alert(`🚨 ${json.triggered_count} Price Alert(s) Triggered! Check your alert status.`);
                }
            } finally {
                evalBtn.disabled = false;
                evalBtn.innerHTML = `<i class="fa-solid fa-bolt"></i> Evaluate Now`;
            }
        });
    }

    const form = document.getElementById("addAlertForm");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const symbol = document.getElementById("alert_symbol").value;
            const condition = document.getElementById("condition").value;
            const target_price = parseFloat(document.getElementById("target_price").value);

            try {
                const res = await fetch("/api/alerts", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ asset_symbol: symbol, condition, target_price })
                });
                const data = await res.json();
                if (res.ok) {
                    modal.classList.remove("active");
                    form.reset();
                    loadAlertsData();
                } else {
                    alert(data.message || "Failed to create alert");
                }
            } catch (err) {
                console.error("Error creating alert:", err);
            }
        });
    }
}

async function loadAlertsData() {
    const tableBody = document.getElementById("alertsTableBody");
    if (!tableBody) return;

    try {
        const res = await fetch("/api/alerts");
        if (res.status === 401) {
            window.location.href = "/login";
            return;
        }
        const json = await res.json();
        const alerts = json.alerts || [];

        const activeCount = alerts.filter(a => a.is_active && !a.is_triggered).length;
        const triggeredCount = alerts.filter(a => a.is_triggered).length;
        document.getElementById("activeAlertsCount").textContent = activeCount;
        document.getElementById("triggeredAlertsCount").textContent = triggeredCount;

        if (alerts.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No alert rules configured. Click 'Create Alert Rule' to set a price threshold.</td></tr>`;
            return;
        }

        tableBody.innerHTML = alerts.map(a => {
            let statusBadge = "";
            if (a.is_triggered) {
                statusBadge = `<span class="asset-badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171;">TRIGGERED</span>`;
            } else if (a.is_active) {
                statusBadge = `<span class="asset-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">MONITORING</span>`;
            } else {
                statusBadge = `<span class="asset-badge" style="background: rgba(156, 163, 175, 0.2); color: #9ca3af;">PAUSED</span>`;
            }

            return `
                <tr>
                    <td><strong>${a.asset_symbol}</strong></td>
                    <td>${a.condition === 'above' ? '≥ Rises Above' : '≤ Drops Below'}</td>
                    <td><strong>$${a.target_price.toLocaleString(undefined, {minimumFractionDigits: 2})}</strong></td>
                    <td>${a.current_price ? `$${a.current_price.toLocaleString(undefined, {minimumFractionDigits: 2})}` : 'N/A'}</td>
                    <td>${statusBadge}</td>
                    <td class="text-muted text-sm">${new Date(a.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="toggleAlert(${a.id})" title="Toggle / Reset">
                            <i class="fa-solid fa-power-off"></i>
                        </button>
                        <button class="btn btn-sm btn-outline text-danger" onclick="deleteAlert(${a.id})" title="Delete">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
    } catch (err) {
        console.error("Error loading alerts:", err);
    }
}

async function toggleAlert(id) {
    try {
        const res = await fetch(`/api/alerts/${id}/toggle`, { method: "POST" });
        if (res.ok) loadAlertsData();
    } catch (err) {
        console.error("Error toggling alert:", err);
    }
}

async function deleteAlert(id) {
    if (!confirm("Are you sure you want to delete this alert rule?")) return;
    try {
        const res = await fetch(`/api/alerts/${id}`, { method: "DELETE" });
        if (res.ok) loadAlertsData();
    } catch (err) {
        console.error("Error deleting alert:", err);
    }
}

// --- AUTH HANDLERS ---
function initAuthForms() {
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const alertBox = document.getElementById("loginAlert");

            try {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });
                const json = await res.json();
                if (res.ok) {
                    window.location.href = "/";
                } else {
                    alertBox.textContent = json.message || "Login failed";
                    alertBox.style.display = "block";
                }
            } catch (err) {
                console.error("Login request error:", err);
            }
        });
    }

    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const alertBox = document.getElementById("registerAlert");

            try {
                const res = await fetch("/api/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });
                const json = await res.json();
                if (res.ok) {
                    window.location.href = "/";
                } else {
                    alertBox.textContent = json.message || "Registration failed";
                    alertBox.style.display = "block";
                }
            } catch (err) {
                console.error("Registration request error:", err);
            }
        });
    }
}

// --- WATCHLIST & TECHNICAL INTELLIGENCE HELPERS ---
async function toggleWatchlist(symbol) {
    try {
        const res = await fetch("/api/market/watchlist", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ asset_symbol: symbol })
        });
        const data = await res.json();
        if (res.status === 201) {
            alert(`Added ${symbol} to your personal Watchlist!`);
        } else if (res.status === 409) {
            // Already present, remove it
            const delRes = await fetch(`/api/market/watchlist/${symbol}`, { method: "DELETE" });
            if (delRes.ok) {
                alert(`Removed ${symbol} from your Watchlist.`);
            }
        } else {
            alert(data.message || "Failed to update watchlist.");
        }
    } catch (err) {
        console.error("Watchlist toggle failed:", err);
    }
}

async function showTechnicalIndicators(symbol) {
    try {
        const res = await fetch(`/api/market/technical/${symbol}`);
        const data = await res.json();
        if (data.status === "success") {
            const ind = data.data;
            alert(`[Technical Analysis: ${ind.symbol}]\nPrice: $${ind.current_price}\nRSI (14): ${ind.rsi_14}\nSMA-7: $${ind.sma_7}\nSMA-14: $${ind.sma_14}\nBollinger Upper: $${ind.bollinger_upper}\nBollinger Lower: $${ind.bollinger_lower}\nSignal: ${ind.signal}\nRationale: ${ind.signal_rationale}`);
        }
    } catch (err) {
        console.error("Failed to fetch technical indicators:", err);
    }
}

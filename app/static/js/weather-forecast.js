/**
 * Ghumna Jam — Trek Weather Forecast
 * Uses Open-Meteo (free, no API key) for current & 7-day conditions.
 */
(function () {
    "use strict";

    const TREK_COORDINATES = {
        1:  { lat: 28.0026, lng: 86.8528, label: "Everest Base Camp" },
        2:  { lat: 28.6667, lng: 84.0167, label: "Annapurna Circuit" },
        3:  { lat: 28.2110, lng: 85.5580, label: "Langtang Valley" },
        4:  { lat: 28.5495, lng: 84.5619, label: "Manaslu Circuit" },
        5:  { lat: 29.1833, lng: 83.9833, label: "Upper Mustang" },
        6:  { lat: 27.9550, lng: 86.6900, label: "Gokyo Lakes & Ri" },
        7:  { lat: 27.7025, lng: 88.1475, label: "Kanchenjunga Base Camp" },
        8:  { lat: 28.4500, lng: 83.9500, label: "Mardi Himal" },
        9:  { lat: 28.4010, lng: 83.6890, label: "Poon Hill Trek" },
        10: { lat: 28.0833, lng: 85.4167, label: "Gosaikunda Lake" },
        11: { lat: 29.5000, lng: 82.1000, label: "Rara Lake Wilderness" },
        12: { lat: 27.8833, lng: 87.0833, label: "Makalu Base Camp" },
        13: { lat: 29.3500, lng: 82.9500, label: "Upper Dolpo Wilderness" },
        14: { lat: 28.8333, lng: 84.1167, label: "Nar Phu Valley" },
        15: { lat: 27.9500, lng: 86.7500, label: "Everest Three Passes" },
    };

    const HOTEL_COORDINATES = {
        "Namche Bazaar":   { lat: 27.8023, lng: 86.7134 },
        "Khumjung":        { lat: 27.8225, lng: 86.7150 },
        "Lobuche":         { lat: 27.9497, lng: 86.8037 },
        "Phakding":        { lat: 27.7417, lng: 86.7139 },
        "Manang":          { lat: 28.6667, lng: 84.0167 },
        "Thorong Phedi":   { lat: 28.7833, lng: 83.9500 },
        "Chame":           { lat: 28.5500, lng: 84.2333 },
        "Braga":           { lat: 28.6833, lng: 84.0167 },
        "Kyanjin Gompa":   { lat: 28.2110, lng: 85.5580 },
        "Langtang Village":{ lat: 28.2333, lng: 85.5167 },
        "Lama Hotel":      { lat: 28.1833, lng: 85.5833 },
        "Syabrubesi":      { lat: 28.1500, lng: 85.3500 },
    };

    const WMO_LABELS = {
        0:  { label: "Clear sky", icon: "☀️", severity: "normal" },
        1:  { label: "Mainly clear", icon: "🌤️", severity: "normal" },
        2:  { label: "Partly cloudy", icon: "⛅", severity: "normal" },
        3:  { label: "Overcast", icon: "☁️", severity: "normal" },
        45: { label: "Fog", icon: "🌫️", severity: "caution" },
        48: { label: "Depositing rime fog", icon: "🌫️", severity: "caution" },
        51: { label: "Light drizzle", icon: "🌦️", severity: "caution" },
        53: { label: "Drizzle", icon: "🌦️", severity: "caution" },
        55: { label: "Dense drizzle", icon: "🌧️", severity: "warning" },
        56: { label: "Freezing drizzle", icon: "🌧️", severity: "warning" },
        57: { label: "Dense freezing drizzle", icon: "🌧️", severity: "warning" },
        61: { label: "Slight rain", icon: "🌧️", severity: "warning" },
        63: { label: "Rain", icon: "🌧️", severity: "warning" },
        65: { label: "Heavy rain", icon: "🌧️", severity: "extreme" },
        66: { label: "Freezing rain", icon: "🌧️", severity: "extreme" },
        67: { label: "Heavy freezing rain", icon: "🌧️", severity: "extreme" },
        71: { label: "Slight snow", icon: "🌨️", severity: "caution" },
        73: { label: "Snow", icon: "🌨️", severity: "warning" },
        75: { label: "Heavy snow", icon: "❄️", severity: "extreme" },
        77: { label: "Snow grains", icon: "🌨️", severity: "caution" },
        80: { label: "Rain showers", icon: "🌦️", severity: "warning" },
        81: { label: "Heavy rain showers", icon: "🌧️", severity: "extreme" },
        82: { label: "Violent rain showers", icon: "⛈️", severity: "extreme" },
        85: { label: "Snow showers", icon: "🌨️", severity: "warning" },
        86: { label: "Heavy snow showers", icon: "❄️", severity: "extreme" },
        95: { label: "Thunderstorm", icon: "⛈️", severity: "extreme" },
        96: { label: "Thunderstorm with hail", icon: "⛈️", severity: "extreme" },
        99: { label: "Thunderstorm with heavy hail", icon: "⛈️", severity: "extreme" },
    };

    function wmoInfo(code) {
        return WMO_LABELS[code] || { label: "Unknown", icon: "🌡️", severity: "normal" };
    }

    function formatDateShort(iso) {
        const d = new Date(iso + "T12:00:00");
        return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
    }

    function formatDayName(iso) {
        const d = new Date(iso + "T12:00:00");
        return d.toLocaleDateString("en-US", { weekday: "short" });
    }

    function addDays(iso, days) {
        const d = new Date(iso + "T12:00:00");
        d.setDate(d.getDate() + days);
        return d.toISOString().slice(0, 10);
    }

    function todayIso() {
        return new Date().toISOString().slice(0, 10);
    }

    function getCoords(destId, hotelLocation) {
        if (hotelLocation && HOTEL_COORDINATES[hotelLocation]) {
            return { ...HOTEL_COORDINATES[hotelLocation], label: hotelLocation };
        }
        return TREK_COORDINATES[destId] || { lat: 27.7172, lng: 85.3240, label: "Nepal Himalayas" };
    }

    function buildAlerts(daily) {
        const alerts = [];
        for (let i = 0; i < daily.time.length; i++) {
            const code = daily.weather_code[i];
            const info = wmoInfo(code);
            const precip = daily.precipitation_sum[i] || 0;
            const wind = daily.wind_speed_10m_max[i] || 0;
            const date = daily.time[i];

            if (info.severity === "extreme") {
                alerts.push({
                    date,
                    type: "extreme",
                    message: `${formatDateShort(date)}: ${info.label} expected — consider rescheduling or extra precautions.`,
                    icon: info.icon,
                });
            } else if (info.severity === "warning" || precip >= 10 || wind >= 50) {
                const parts = [];
                if (info.severity === "warning") parts.push(info.label);
                if (precip >= 10) parts.push(`heavy precipitation (${precip.toFixed(1)} mm)`);
                if (wind >= 50) parts.push(`strong winds (${wind.toFixed(0)} km/h)`);
                alerts.push({
                    date,
                    type: "warning",
                    message: `${formatDateShort(date)}: ${parts.join(", ")}.`,
                    icon: precip >= 10 ? "🌧️" : wind >= 50 ? "💨" : info.icon,
                });
            }
        }
        return alerts;
    }

    async function fetchForecast(lat, lng, startDate, endDate) {
        const params = new URLSearchParams({
            latitude: lat,
            longitude: lng,
            current: "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation",
            daily: "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            timezone: "auto",
        });

        if (startDate && endDate) {
            params.set("start_date", startDate);
            params.set("end_date", endDate);
        } else {
            params.set("forecast_days", "7");
        }

        const url = `https://api.open-meteo.com/v1/forecast?${params.toString()}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error("Weather data unavailable");
        return response.json();
    }

    function renderAlerts(container, alerts) {
        if (!container) return;
        if (!alerts.length) {
            container.classList.add("hidden");
            container.innerHTML = "";
            return;
        }
        container.classList.remove("hidden");
        const hasExtreme = alerts.some((a) => a.type === "extreme");
        container.className = hasExtreme
            ? "rounded-xl border border-red-200 bg-red-50 p-4 space-y-2"
            : "rounded-xl border border-amber-200 bg-amber-50 p-4 space-y-2";

        container.innerHTML = `
            <div class="flex items-center gap-2">
                <span class="text-lg">${hasExtreme ? "⚠️" : "🔔"}</span>
                <span class="text-xs font-bold uppercase tracking-wider ${hasExtreme ? "text-red-800" : "text-amber-800"}">
                    Weather Alerts
                </span>
            </div>
            <ul class="space-y-1.5">
                ${alerts.map((a) => `
                    <li class="text-xs ${a.type === "extreme" ? "text-red-700 font-semibold" : "text-amber-800"} flex items-start gap-2">
                        <span>${a.icon}</span>
                        <span>${a.message}</span>
                    </li>
                `).join("")}
            </ul>
        `;
    }

    function renderCurrent(container, current, locationLabel) {
        if (!container || !current) return;
        const info = wmoInfo(current.weather_code);
        container.innerHTML = `
            <div class="flex items-center justify-between gap-4">
                <div>
                    <span class="block text-[10px] uppercase font-bold tracking-wider text-gray-400 mb-1">Current Conditions</span>
                    <span class="block text-xs text-gray-500 mb-2">${locationLabel}</span>
                    <div class="flex items-center gap-3">
                        <span class="text-4xl">${info.icon}</span>
                        <div>
                            <span class="block text-2xl font-bold text-brandGreen">${Math.round(current.temperature_2m)}°C</span>
                            <span class="block text-sm text-gray-600">${info.label}</span>
                        </div>
                    </div>
                </div>
                <div class="text-right text-xs text-gray-500 space-y-1">
                    <div>💧 Humidity <span class="font-semibold text-gray-700">${current.relative_humidity_2m}%</span></div>
                    <div>💨 Wind <span class="font-semibold text-gray-700">${Math.round(current.wind_speed_10m)} km/h</span></div>
                    <div>🌧️ Precip <span class="font-semibold text-gray-700">${(current.precipitation || 0).toFixed(1)} mm</span></div>
                </div>
            </div>
        `;
    }

    function renderDailyGrid(container, daily, selectedDate) {
        if (!container || !daily) return;
        const today = todayIso();

        container.innerHTML = daily.time.map((date, i) => {
            const info = wmoInfo(daily.weather_code[i]);
            const isSelected = selectedDate && date === selectedDate;
            const isToday = date === today;
            const ring = isSelected
                ? "ring-2 ring-brandYellow border-brandGreen bg-brandGreen/5"
                : isToday
                    ? "border-brandGreen/30 bg-gray-50"
                    : "border-gray-100 bg-white";

            return `
                <div class="rounded-xl border p-3 text-center transition ${ring}" data-weather-date="${date}">
                    <span class="block text-[10px] font-bold uppercase tracking-wider ${isSelected ? "text-brandGreen" : "text-gray-400"}">
                        ${isSelected ? "Departure" : isToday ? "Today" : formatDayName(date)}
                    </span>
                    <span class="block text-lg my-1">${info.icon}</span>
                    <span class="block text-[10px] text-gray-500 mb-1">${formatDateShort(date)}</span>
                    <span class="block text-xs font-bold text-brandGreen">${Math.round(daily.temperature_2m_max[i])}° / ${Math.round(daily.temperature_2m_min[i])}°</span>
                    <span class="block text-[10px] text-gray-400 mt-1">${info.label}</span>
                    ${daily.precipitation_sum[i] > 0 ? `<span class="block text-[9px] text-blue-600 mt-0.5">🌧 ${daily.precipitation_sum[i].toFixed(1)} mm</span>` : ""}
                </div>
            `;
        }).join("");
    }

    function renderSelectedDay(container, daily, selectedDate) {
        if (!container) return;
        if (!selectedDate) {
            container.classList.add("hidden");
            container.innerHTML = "";
            return;
        }

        const idx = daily.time.indexOf(selectedDate);
        if (idx === -1) {
            container.classList.remove("hidden");
            container.innerHTML = `
                <div class="rounded-xl border border-gray-200 bg-gray-50 p-4 text-xs text-gray-500">
                    Selected departure date is outside the loaded forecast window. Choose a date within the next 16 days for detailed conditions.
                </div>
            `;
            return;
        }

        const info = wmoInfo(daily.weather_code[idx]);
        const isExtreme = info.severity === "extreme" || info.severity === "warning";

        container.classList.remove("hidden");
        container.innerHTML = `
            <div class="rounded-xl border ${isExtreme ? "border-amber-300 bg-amber-50" : "border-brandGreen/20 bg-brandGreen/5"} p-4">
                <span class="block text-[10px] uppercase font-bold tracking-wider text-brandGreen mb-2">Departure Day Forecast</span>
                <div class="flex items-center gap-4">
                    <span class="text-3xl">${info.icon}</span>
                    <div>
                        <span class="block font-semibold text-brandGreen">${formatDateShort(selectedDate)}</span>
                        <span class="block text-sm text-gray-600">${info.label}</span>
                        <span class="block text-xs text-gray-500 mt-1">
                            High ${Math.round(daily.temperature_2m_max[idx])}°C · Low ${Math.round(daily.temperature_2m_min[idx])}°C ·
                            Wind up to ${Math.round(daily.wind_speed_10m_max[idx])} km/h
                            ${daily.precipitation_sum[idx] > 0 ? ` · Rain ${daily.precipitation_sum[idx].toFixed(1)} mm` : ""}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    function renderCardContent(container, daily, destName) {
        if (!container || !daily) return;
        const alerts = buildAlerts(daily);
        const alertDot = alerts.length
            ? `<span class="inline-flex items-center gap-1 text-[9px] font-bold text-red-600 bg-red-50 px-1.5 py-0.5 rounded-full">⚠ ${alerts.length} alert${alerts.length > 1 ? "s" : ""}</span>`
            : "";

        container.innerHTML = `
            <div class="border-t border-gray-50 pt-3 mt-1">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-[10px] uppercase font-bold tracking-wider text-gray-400">7-Day Climate</span>
                    ${alertDot}
                </div>
                <div class="grid grid-cols-7 gap-1">
                    ${daily.time.map((date, i) => {
                        const info = wmoInfo(daily.weather_code[i]);
                        const hasAlert = info.severity === "extreme" || info.severity === "warning";
                        return `
                            <div class="text-center ${hasAlert ? "bg-red-50 rounded" : ""}" title="${formatDateShort(date)}: ${info.label}">
                                <span class="block text-[8px] text-gray-400 font-medium">${formatDayName(date).slice(0, 3)}</span>
                                <span class="block text-sm leading-tight">${info.icon}</span>
                                <span class="block text-[8px] font-bold text-brandGreen">${Math.round(daily.temperature_2m_max[i])}°</span>
                            </div>
                        `;
                    }).join("")}
                </div>
                <span class="block text-[9px] text-gray-400 mt-2 truncate" title="${destName}">${destName} region</span>
            </div>
        `;
    }

    function setLoading(widget, isLoading) {
        const loader = widget.querySelector("[data-weather-loading]");
        const content = widget.querySelector("[data-weather-content]");
        if (loader) loader.classList.toggle("hidden", !isLoading);
        if (content) content.classList.toggle("hidden", isLoading);
    }

    function showContent(widget) {
        widget.querySelector("[data-weather-loading]")?.classList.add("hidden");
        widget.querySelector("[data-weather-content]")?.classList.remove("hidden");
    }

    function setError(widget, message) {
        const errorEl = widget.querySelector("[data-weather-error]");
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove("hidden");
        }
        setLoading(widget, false);
    }

    async function loadDetailForecast(widget) {
        const destId = parseInt(widget.dataset.destId, 10);
        const dateInput = document.getElementById(widget.dataset.dateInputId || "departure_date");
        const selectedDate = dateInput && dateInput.value ? dateInput.value : null;

        const hotelRadio = document.querySelector('input[name="selected_hotel"]:checked');
        let hotelLocation = null;
        if (hotelRadio) {
            const label = hotelRadio.closest("label");
            const locSpan = label && label.querySelector(".text-gray-500");
            if (locSpan) {
                const text = locSpan.textContent || "";
                for (const name of Object.keys(HOTEL_COORDINATES)) {
                    if (text.includes(name)) {
                        hotelLocation = name;
                        break;
                    }
                }
            }
        }

        const coords = getCoords(destId, hotelLocation);
        const locationLabel = widget.querySelector("[data-weather-location]");
        if (locationLabel) locationLabel.textContent = coords.label;

        let startDate = null;
        let endDate = null;
        if (selectedDate) {
            startDate = selectedDate;
            endDate = addDays(selectedDate, 6);
        }

        setLoading(widget, widget.querySelector("[data-weather-content]")?.classList.contains("hidden"));
        const errorEl = widget.querySelector("[data-weather-error]");
        if (errorEl) errorEl.classList.add("hidden");

        try {
            const data = await fetchForecast(coords.lat, coords.lng, startDate, endDate);
            const alerts = buildAlerts(data.daily);

            renderCurrent(widget.querySelector("[data-weather-current]"), data.current, coords.label);
            renderAlerts(widget.querySelector("[data-weather-alerts]"), alerts);
            renderSelectedDay(widget.querySelector("[data-weather-selected]"), data.daily, selectedDate);
            renderDailyGrid(widget.querySelector("[data-weather-daily]"), data.daily, selectedDate);
            showContent(widget);
        } catch (err) {
            setError(widget, "Unable to load weather forecast. Please check your connection and try again.");
            console.error("Weather forecast error:", err);
        }
    }

    async function loadCardForecast(widget) {
        const destId = parseInt(widget.dataset.destId, 10);
        const coords = getCoords(destId, null);

        try {
            const data = await fetchForecast(coords.lat, coords.lng, null, null);
            renderCardContent(widget.querySelector("[data-weather-card-body]"), data.daily, coords.label);
            widget.querySelector("[data-weather-card-loading]")?.classList.add("hidden");
            widget.querySelector("[data-weather-card-body]")?.classList.remove("hidden");
        } catch (err) {
            const body = widget.querySelector("[data-weather-card-body]");
            if (body) {
                body.classList.remove("hidden");
                body.innerHTML = `<span class="text-[10px] text-gray-400">Climate data unavailable</span>`;
            }
            widget.querySelector("[data-weather-card-loading]")?.classList.add("hidden");
        }
    }

    function initDetail(widget) {
        if (!widget) return;

        const dateInputId = widget.dataset.dateInputId || "departure_date";
        const dateInput = document.getElementById(dateInputId);

        const refresh = () => loadDetailForecast(widget);
        refresh();

        if (dateInput) {
            dateInput.addEventListener("change", refresh);
            dateInput.addEventListener("input", refresh);
        }

        document.querySelectorAll('input[name="selected_hotel"]').forEach((radio) => {
            radio.addEventListener("change", refresh);
        });
    }

    function initCards() {
        document.querySelectorAll("[data-trek-weather-card]").forEach((widget) => {
            loadCardForecast(widget);
        });
    }

    function initAll() {
        document.querySelectorAll("[data-trek-weather-detail]").forEach((widget) => {
            if (!widget.dataset.weatherInitialized) {
                widget.dataset.weatherInitialized = "true";
                initDetail(widget);
            }
        });
        document.querySelectorAll("[data-trek-weather-card]").forEach((widget) => {
            if (!widget.dataset.weatherInitialized) {
                widget.dataset.weatherInitialized = "true";
                loadCardForecast(widget);
            }
        });
    }

    window.GhumnaJamWeather = {
        initAll,
        initDetail,
        initCards,
        loadDetailForecast,
        loadCardForecast,
        getCoords,
        TREK_COORDINATES,
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initAll);
    } else {
        initAll();
    }
})();

document.addEventListener("DOMContentLoaded", () => {

    const btn = document.getElementById("locationBtn");
    const form = document.querySelector("form");
    const loading = document.getElementById("loadingScreen");
    const predictBtn = document.getElementById("predictBtn");

    let map = null;

    // ==============================
    // GET CURRENT WEATHER
    // ==============================

    btn.addEventListener("click", () => {

        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser.");
            return;
        }

        btn.disabled = true;
        btn.innerHTML = "⏳ Fetching Weather...";

        navigator.geolocation.getCurrentPosition(success, error);

    });

    // ==============================
    // SUCCESS
    // ==============================

    function success(position) {

        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        // --------------------------
        // CREATE MAP
        // --------------------------

        if (map) {
            map.remove();
        }

        map = L.map("map").setView([lat, lon], 13);

        setTimeout(() => {
            map.invalidateSize();
        }, 200);

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution: "&copy; OpenStreetMap contributors"
            }
        ).addTo(map);

        delete L.Icon.Default.prototype._getIconUrl;

        L.Icon.Default.mergeOptions({

            iconRetinaUrl:
                "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

            iconUrl:
                "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

            shadowUrl:
                "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png"

        });

        L.marker([lat, lon])
            .addTo(map)
            .bindPopup("📍 Your Current Location")
            .openPopup();

        // --------------------------
        // FETCH WEATHER
        // --------------------------

        fetch("/weather", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                lat,
                lon
            })

        })

        .then(response => {

            if (!response.ok) {
                throw new Error("Weather request failed.");
            }

            return response.json();

        })

        .then(data => {

            document.querySelector('input[name="temperature"]').value = data.temperature;

            document.querySelector('input[name="humidity"]').value = data.humidity;

            document.querySelector('input[name="rainfall"]').value = data.rainfall;

            document.getElementById("weatherInfo").innerHTML = `

            <div class="weather-grid">

                <div class="weather-box">
                    <h4>📍 Location</h4>
                    <p>${data.city}</p>
                </div>

                <div class="weather-box">
                    <h4>🌡 Temperature</h4>
                    <p>${data.temperature} °C</p>
                </div>

                <div class="weather-box">
                    <h4>💧 Humidity</h4>
                    <p>${data.humidity}%</p>
                </div>

                <div class="weather-box">
                    <h4>🌧 Rainfall</h4>
                    <p>${data.rainfall} mm</p>
                </div>

                <div class="weather-box">
                    <h4>💨 Wind Speed</h4>
                    <p>${data.wind_speed} m/s</p>
                </div>

            </div>

            `;

        })

        .catch(err => {

            console.error(err);

            alert("Unable to fetch weather information.");

        })

        .finally(() => {

            btn.disabled = false;
            btn.innerHTML = "📍 Get Current Weather";

        });

    }

    // ==============================
    // LOCATION ERROR
    // ==============================

    function error(err) {

        btn.disabled = false;
        btn.innerHTML = "📍 Get Current Weather";

        alert("Location access denied.");

        console.error(err);

    }

    // ==============================
    // LOADING SCREEN
    // ==============================

    if (form) {

        form.addEventListener("submit", () => {

            loading.style.display = "flex";

            predictBtn.disabled = true;

            const texts = [

                "Collecting Weather Data...",

                "Analyzing Rainfall...",

                "Checking River Conditions...",

                "Running Machine Learning Model...",

                "Calculating Flood Probability...",

                "Generating AI Report..."

            ];

            let i = 0;

            const loadingText =
                document.getElementById("loadingText");

            loadingText.innerHTML = texts[0];

            const interval = setInterval(() => {

                i++;

                if (i < texts.length) {

                    loadingText.innerHTML = texts[i];

                } else {

                    clearInterval(interval);

                }

            }, 800);

        });

    }

});
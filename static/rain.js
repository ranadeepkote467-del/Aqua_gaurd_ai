document.addEventListener("DOMContentLoaded", () => {

    const btn = document.getElementById("locationBtn");

    btn.addEventListener("click", () => {

        if (!navigator.geolocation) {
            alert("Geolocation is not supported.");
            return;
        }

        navigator.geolocation.getCurrentPosition(success, error);

    });

});

function success(position) {

    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    fetch("/weather", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            lat: lat,
            lon: lon
        })

    })

    .then(response => response.json())

    .then(data => {
        

        // Auto-fill form
        document.querySelector('input[name="temperature"]').value = data.temperature;
        document.querySelector('input[name="humidity"]').value = data.humidity;
        document.querySelector('input[name="rainfall"]').value = data.rainfall;

        // Display weather
        document.getElementById("weatherInfo").innerHTML = `

        <div class="weather-grid">

            <div class="weather-box">
                <h4>📍 City</h4>
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

    .catch(error => {
        console.error(error);
        alert("Unable to fetch weather.");
    });

}

function error(err) {

    alert("Location access denied.");

    console.log(err);

}
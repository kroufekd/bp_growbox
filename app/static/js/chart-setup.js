$(document).ready(function(){
		var tempCtx = document.getElementById('temperatureChart').getContext('2d');
    var tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: chartData.timestamps,
            datasets: [{
                label: 'Temperature (°C)',
                data: chartData.temperatures,
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });

    var humidCtx = document.getElementById('humidityChart').getContext('2d');
    var humidChart = new Chart(humidCtx, {
        type: 'line',
        data: {
            labels: chartData.timestamps,
            datasets: [{
                label: 'Humidity (%)',
                data: chartData.humidities,
                borderColor: '#033A6B',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
});

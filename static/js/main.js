$(document).ready(function(){
            function fetchData() {
                $.getJSON('/data', function(data) {
                    $('#temperature').text(data.temperature + ' °C');
                    $('#humidity').text(data.humidity + ' %');
                });
            }

            $('#fanOn').click(function(){
                $.ajax({
                    url: '/fan',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({state: 'on'}),
                    success: function(response) {
                        console.log('Fan turned on');
                    }
                });
            });

            $('#fanOff').click(function(){
                $.ajax({
                    url: '/fan',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({state: 'off'}),
                    success: function(response) {
                        console.log('Fan turned off');
                    }
                });
            });

            fetchData();
            //setInterval(fetchData, 60000); // Refresh every 10 seconds
        });

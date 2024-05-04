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
            $('#fanControlForm').on('submit', function(e) {
            e.preventDefault(); // Prevent the default form submission
            var frequency = $('#frequency').val();
            var period = $('#period').val();

            $.ajax({
                type: 'POST',
                url: '/set_schedule',
                contentType: 'application/json',
                data: JSON.stringify({ frequency: frequency, period: period }),
                success: function(response) {
                    alert('Schedule has been updated successfully!');
                },
                error: function() {
                    alert('Error updating schedule');
                }
            });
        });

            fetchData();
            setInterval(fetchData,30000); // Refresh every 10 seconds
        });

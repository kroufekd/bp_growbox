from flask import render_template, jsonify, request, Response
from . import app
from .camera.camera import generate_frames
from .fan_control.fan import update_scheduler, turn_fan_on, turn_fan_off, update_scheduler_from_db
from .database.db import get_db_connection
from datetime import datetime, timedelta
   
@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor()
    
    # načtení nastevní větráčku
    cursor.execute("SELECT frequency, period FROM FanSettings ORDER BY id DESC LIMIT 1")
    settings = cursor.fetchone()
    frequency, period = settings if settings else (1, 'hourly')
    
    # načtení dat ze senzorů
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    cursor.execute("SELECT temperature, humidity, timestamp FROM sensor_readings WHERE timestamp >= %s", (twenty_four_hours_ago,))
    readings = cursor.fetchall()
    
    cursor.close()
    db.close()

    # úprava dat pro chart.js
    temperatures = [reading[0] for reading in readings]
    humidities = [reading[1] for reading in readings]
    timestamps = [reading[2].strftime('%Y-%m-%d %H:%M:%S') for reading in readings]

    return render_template('index.html', frequency=frequency, period=period,
                           temperatures=temperatures, humidities=humidities, timestamps=timestamps)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_schedule', methods=['POST']) #route pro nastavení frekvence větrání
def set_schedule():
    data = request.get_json()
    frequency = int(data['frequency'])
    period = data['period']
    db = get_db_connection()
    with db.cursor() as cursor:
        cursor.execute("INSERT INTO FanSettings (frequency, period) VALUES (%s, %s)", (frequency, period))
        db.commit()
    db.close()
    update_scheduler(frequency, period)
    return jsonify({'message': 'Schedule updated successfully'})

@app.route('/data') # get route pro ziskani dat ze senzoru teplota/vlhkost
def data():
    db = get_db_connection()
    from Adafruit_DHT import read_retry, DHT22
    sensor = DHT22
    pin = 4
    humidity, temperature = read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        with db.cursor() as cursor:
            sql = "INSERT INTO sensor_readings (temperature, humidity) VALUES (%s, %s)"
            cursor.execute(sql, (temperature, humidity))
            db.commit()
        db.close()
        return jsonify({'temperature': f"{temperature:.1f}", 'humidity': f"{humidity:.1f}"})
    db.close()
    return jsonify({'temperature': 'Error', 'humidity': 'Error'})

from flask import Flask, render_template, jsonify, request, Response
import Adafruit_DHT
import RPi.GPIO as GPIO
import io
import picamera
import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

# Initialize Flask app
app = Flask(__name__)

# GPIO setup
GPIO.setmode(GPIO.BCM)
relay_pin = 3  # Adjust to your GPIO setup
GPIO.setup(relay_pin, GPIO.OUT)

# DHT22 sensor setup
sensor = Adafruit_DHT.DHT22
pin = 4  # GPIO pin connected to DHT22 sensor

# Database connection setup
db = mysql.connector.connect(
    host="localhost",
    user="growbox_user",
    password="Cisco123",
    database="growbox"
)

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.start()

# Function to generate camera frames
def generate_frames():
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        stream = io.BytesIO()

        for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            stream.seek(0)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')
            stream.seek(0)
            stream.truncate()

# Home page route
@app.route('/')
def index():
    with db.cursor() as cursor:
        cursor.execute("SELECT frequency, period FROM FanSettings ORDER BY id DESC LIMIT 1")
        current_settings = cursor.fetchone()
    return render_template('index.html', current_settings=current_settings)

# Route for video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to retrieve and store sensor data
@app.route('/data')
def data():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        with db.cursor() as cursor:
            sql = "INSERT INTO sensor_readings (temperature, humidity) VALUES (%s, %s)"
            cursor.execute(sql, (temperature, humidity))
            db.commit()
        return jsonify({'temperature': f"{temperature:.1f}", 'humidity': f"{humidity:.1f}"})
    return jsonify({'temperature': 'Error', 'humidity': 'Error'})

# Route to set the fan schedule
@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    data = request.get_json()
    frequency = int(data['frequency'])
    period = data['period']
    with db.cursor() as cursor:
        cursor.execute("INSERT INTO FanSettings (frequency, period) VALUES (%s, %s)", (frequency, period))
        db.commit()
    update_scheduler(frequency, period)
    return jsonify({'message': 'Schedule updated successfully'})

# Functions to control the fan
def turn_fan_on():
    GPIO.output(relay_pin, GPIO.LOW)
    print("Fan ON")
    scheduler.add_job(turn_fan_off, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=1), id='fan_off_job')

def turn_fan_off():
    GPIO.output(relay_pin, GPIO.HIGH)
    print("Fan OFF")

# Update scheduler based on database settings
def update_scheduler(frequency, period):
    scheduler.remove_all_jobs()
    interval = datetime.timedelta(hours=1/frequency) if period == 'hourly' else datetime.timedelta(days=1/frequency)
    scheduler.add_job(turn_fan_on, trigger='interval', next_run_time=datetime.datetime.now(), seconds=interval.total_seconds(), id='fan_job')

def update_scheduler_from_db():
    with db.cursor() as cursor:
        cursor.execute("SELECT frequency, period FROM FanSettings ORDER BY id DESC LIMIT 1")
        settings = cursor.fetchone()
    if settings:
        update_scheduler(settings[0], settings[1])

# Main entry point for the Flask application
if __name__ == '__main__':
    update_scheduler_from_db()
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)

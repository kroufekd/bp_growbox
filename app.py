from flask import Flask, render_template, jsonify, request, Response
import Adafruit_DHT
import RPi.GPIO as GPIO
import io
import picamera
import mysql.connector

app = Flask(__name__)

# GPIO setup
GPIO.setmode(GPIO.BCM)
relay_pin = 23  # Adjust to your GPIO setup
GPIO.setup(relay_pin, GPIO.OUT)

# DHT22 setup
sensor = Adafruit_DHT.DHT22
pin = 4  # Adjust to your GPIO pin setup

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="growbox_user",
    password="Cisco123",
    database="growbox"
)

cursor = db.cursor()

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
		# Insert data into the database
        sql = "INSERT INTO sensor_readings (temperature, humidity) VALUES (%s, %s)"
        val = (temperature, humidity)
        cursor.execute(sql, val)
        db.commit()
        
        return jsonify({'temperature': f"{temperature:.1f}", 'humidity': f"{humidity:.1f}"})
    else:
        return jsonify({'temperature': 'Error', 'humidity': 'Error'})

@app.route('/fan', methods=['POST'])
def fan():
    state = request.json['state']
    if state == "on":
        GPIO.output(relay_pin, GPIO.LOW)
    elif state == "off":
        GPIO.output(relay_pin, GPIO.HIGH)
    return jsonify({'status': 'success'})

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)

import RPi.GPIO as GPIO
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app import app

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Setup GPIO for fan control
GPIO.setmode(GPIO.BCM)
relay_pin = 3  # Adjust as per your specific GPIO setup
GPIO.setup(relay_pin, GPIO.OUT)

def turn_fan_on():
    """Function to turn the fan on and schedule to turn it off after 1 minute."""
    GPIO.output(relay_pin, GPIO.LOW)
    print("Fan ON")

    # Remove the existing 'fan_off_job' if it exists
    if scheduler.get_job('fan_off_job'):
        scheduler.remove_job('fan_off_job')

    # Schedule to turn the fan off after 1 minute
    scheduler.add_job(turn_fan_off, 'date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=1), id='fan_off_job')

def turn_fan_off():
    """Function to turn the fan off."""
    GPIO.output(relay_pin, GPIO.HIGH)
    print("Fan OFF")

def update_scheduler(frequency, period):
    """Update or create a scheduler based on user input for frequency and period."""
    # Clear all existing jobs to reset the schedule
    scheduler.remove_all_jobs()

    # Calculate the interval based on user input
    interval = datetime.timedelta(hours=1/frequency) if period == 'hourly' else datetime.timedelta(days=1/frequency)

    # Schedule the fan to turn on at the calculated interval
    scheduler.add_job(turn_fan_on, trigger='interval', next_run_time=datetime.datetime.now(), seconds=interval.total_seconds(), id='fan_job')

def update_scheduler_from_db():
    """Update the scheduler with settings from the database at startup."""
    from .database.db import get_db_connection
    db = get_db_connection()
    with db.cursor() as cursor:
        cursor.execute("SELECT frequency, period FROM fan_settings ORDER BY id DESC LIMIT 1")
        settings = cursor.fetchone()

    if settings:
        update_scheduler(settings[0], settings[1])

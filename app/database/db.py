import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="growbox_user",
        password="Cisco123",
        database="growbox"
    )

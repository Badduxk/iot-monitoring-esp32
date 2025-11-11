from flask import Flask, render_template, redirect, jsonify
from paho.mqtt import client as mqtt
import mysql.connector

# MQTT CONFIG
BROKER = "broker.hivemq.com"
TOPIC_LED = "coba/led"   

mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, 1883)

# RELAY STATE
relay_state = "unknown"

# FLASK APP
app = Flask(__name__)


# Fungsi: Ambil semua data 
def get_all_data():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="iot"
        )
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, temperature, humidity, brightness AS light,
                   waktu AS timestamp
            FROM data_sensor
            ORDER BY id DESC LIMIT 10
        """)

        result = cursor.fetchall()
        db.close()
        return result

    except mysql.connector.Error as e:
        print("DB ERROR:", e)
        return []

# Fungsi: Ambil data terbaru
def get_latest_data():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="iot"
        )
        cursor = db.cursor()

        cursor.execute("""
            SELECT temperature, humidity, brightness, waktu
            FROM data_sensor
            ORDER BY id DESC LIMIT 1
        """)

        result = cursor.fetchone()
        db.close()

        if result:
            return {
                "temperature": result[0],
                "humidity": result[1],
                "brightness": result[2],
                "time": str(result[3])
            }

        return None

    except mysql.connector.Error as e:
        print("DB ERROR:", e)
        return None


# ================================
# ROUTES / ENDPOINTS
# ================================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    return jsonify(get_all_data())


@app.route("/api/latest")
def api_latest():
    return jsonify(get_latest_data())


# ================================
# RELAY CONTROL
# ================================
@app.route("/led/<status>")
def control_led(status):
    global relay_state
    mqtt_client.publish(TOPIC_LED, status)
    relay_state = status
    return jsonify({"status": relay_state})


@app.route("/api/relay_status")
def api_relay_status():
    return jsonify({"status": relay_state})


# ================================
# RUN SERVER
# ================================
if __name__ == "__main__":
    app.run(debug=True)

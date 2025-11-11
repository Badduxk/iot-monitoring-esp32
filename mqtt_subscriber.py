import json
import time
from paho.mqtt import client as mqtt
from database import insert_data

BROKER = "broker.hivemq.com"
TOPIC_SUHU = "coba/suhu"
TOPIC_LDR  = "coba/ldr"
TOPIC_RELAY = "coba/relay"   

# BUFFER DATA SEMENTARA
buffer_data = {
    "temperature": None,
    "humidity": None,
    "brightness": None
}

def try_insert():
    """Jika semua data sudah ada, insert ke database dan reset buffer"""
    if (buffer_data["temperature"] is not None and
        buffer_data["humidity"] is not None and
        buffer_data["brightness"] is not None):

        print("✅ INSERT:", buffer_data)
        insert_data(
            buffer_data["temperature"],
            buffer_data["humidity"],
            buffer_data["brightness"]
        )

        # Reset buffer
        buffer_data["temperature"] = None
        buffer_data["humidity"] = None
        buffer_data["brightness"] = None


def on_message(client, userdata, msg):
    print(f"[MQTT] {msg.topic} => {msg.payload.decode()}")

   
    # PERINTAH RELAY DARI WEB DASHBOARD
    if msg.topic == TOPIC_RELAY:
        command = msg.payload.decode().upper()
        print(f"🚨 PERINTAH RELAY DITERIMA DARI WEB: {command}")

        return

    # DATA SENSOR
    try:
        data = json.loads(msg.payload.decode())
    except:
        print("❌ Payload bukan JSON!")
        return

    #DATA DARI TOPIC SUHU 
    if msg.topic == TOPIC_SUHU:
        buffer_data["temperature"] = data.get("temperature")
        buffer_data["humidity"] = data.get("humidity")

    #DATA DARI TOPIC LDR
    elif msg.topic == TOPIC_LDR:
        buffer_data["brightness"] = data.get("brightness")

    # Setelah update, cek apakah semua data sudah lengkap
    try_insert()


def main():
    client = mqtt.Client()
    client.on_message = on_message

    print("🔌 Menghubungkan ke MQTT Broker...")
    client.connect(BROKER, 1883)

    print("📡 Subscribe ke topik...")
    client.subscribe(TOPIC_SUHU)
    client.subscribe(TOPIC_LDR)
    client.subscribe(TOPIC_RELAY)  # SUBSCRIBE TOPIK RELAY BARU

    print("✅ MQTT Subscriber berjalan...\n")

    client.loop_forever()


if __name__ == "__main__":
    main()

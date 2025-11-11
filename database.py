import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="iot"
    )

def insert_data(temp, hum, brightness):
    db = connect_db()
    cursor = db.cursor()

    sql = """
    INSERT INTO data_sensor (temperature, humidity, brightness)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (temp, hum, brightness))
    db.commit()
    db.close()

    print("✅ Data berhasil disimpan ke database!")

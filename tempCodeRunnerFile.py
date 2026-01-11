def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="habit_db"
    )
import datetime
import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd

# Connect to MySQL
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # change to your MySQL username
        password="123456",    # change to your MySQL password
        database="habit_db"
    )

# Add habit
def add_habit(habit_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO habits (name) VALUES (%s)", (habit_name,))
        conn.commit()
        print(f"✅ Habit '{habit_name}' added!")
    except:
        print("⚠️ Habit already exists.")
    cur.close()
    conn.close()

# Log habit
def log_habit(habit_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM habits WHERE name=%s", (habit_name,))
    result = cur.fetchone()
    if result:
        habit_id = result[0]
        today = datetime.date.today()
        try:
            cur.execute("INSERT INTO logs (habit_id, date) VALUES (%s, %s)", (habit_id, today))
            conn.commit()
            print(f"✅ Logged '{habit_name}' for {today}")
        except:
            print("⚠️ Already logged today.")
    else:
        print("❌ Habit not found.")
    cur.close()
    conn.close()

# View progress (with graph)
def view_progress():
    conn = get_connection()
    query = """
        SELECT h.name, COUNT(l.id) AS count
        FROM habits h
        LEFT JOIN logs l ON h.id = l.habit_id
        GROUP BY h.name
    """
    df = pd.read_sql(query, conn)
    conn.close()

    print("\n📊 Progress Report")
    for _, row in df.iterrows():
        print(f"- {row['name']}: {row['count']} days completed")

    if not df.empty:
        plt.bar(df['name'], df['count'], color='green')
        plt.xlabel("Habits")
        plt.ylabel("Days Completed")
        plt.title("Habit Progress")
        plt.show()

# Menu
while True:
    print("\n--- Habit Tracker ---")
    print("1. Add Habit")
    print("2. Log Habit")
    print("3. View Progress (Graph)")
    print("4. Exit")
    choice = input("Enter choice: ")

    if choice == "1":
        name = input("Enter habit name: ")
        add_habit(name)
    elif choice == "2":
        name = input("Enter habit name to log: ")
        log_habit(name)
    elif choice == "3":
        view_progress()
    elif choice == "4":
        print("👋 Exiting Habit Tracker...")
        break
    else:
        print("⚠️ Invalid choice. Try again.")
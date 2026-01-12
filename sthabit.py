import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# DB connection + bootstrap
# -----------------------------
DB_PATH = "habit_db.sqlite"

def get_connection():
    # SQLite file-based DB (repo ke andar)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Habits table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Logs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# -----------------------------
# Helpers
# -----------------------------
def add_habit(habit_name: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # SQLite parameter placeholder = "?"
        cur.execute("INSERT INTO habits (name) VALUES (?)", (habit_name,))
        conn.commit()
        return True, f"Habit '{habit_name}' added!"
    except sqlite3.IntegrityError:
        return False, f"Habit '{habit_name}' already exists."
    except sqlite3.Error as e:
        return False, f"Could not add habit: {e}"
    finally:
        cur.close()
        conn.close()

def get_habits_df() -> pd.DataFrame:
    conn = get_connection()
    # Use read_sql_query for SQLite
    df = pd.read_sql_query("SELECT id, name FROM habits ORDER BY name", conn)
    conn.close()
    return df

def log_habit(habit_name: str):
    conn = get_connection()
    cur = conn.cursor()

    # Find habit id (SQLite placeholder "?")
    cur.execute("SELECT id FROM habits WHERE name = ?", (habit_name,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return False, "Habit not found."

    habit_id = row[0]

    try:
        # SQLite: use DATE('now') instead of CURDATE()
        cur.execute(
            "INSERT INTO logs (habit_id, date) VALUES (?, DATE('now'))",
            (habit_id,)
        )
        conn.commit()
        return True, f"Logged '{habit_name}' for today."
    except sqlite3.Error as e:
        return False, f"Could not log habit: {e}"
    finally:
        cur.close()
        conn.close()

def get_progress_df() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT h.name AS habit, COUNT(l.id) AS count
        FROM habits h
        LEFT JOIN logs l ON h.id = l.habit_id
        GROUP BY h.name
        ORDER BY h.name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# -----------------------------
# Streamlit UI
# -----------------------------
# Init DB on app start
init_db()

st.set_page_config(page_title="Habit Tracker", page_icon="🌱", layout="centered")

# 🎨 Gradient theme
custom_css = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #6a11cb 0%, #2575fc 100%);
}
h1, h2, h3 {
    color: #ffffff;
    text-shadow: 2px 2px 8px #000000;
}
button, .stButton>button {
    background: linear-gradient(90deg, #ff6a00, #ee0979);
    color: white;
    border-radius: 12px;
    box-shadow: 0px 0px 12px #00c9ff;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🌱 Habit Tracker (SQLite + Streamlit)")

menu = st.sidebar.radio("Navigation", ["Add Habit", "Log Habit", "View Progress"])

# Add Habit
if menu == "Add Habit":
    st.subheader("➕ Add a new habit")
    habit_name = st.text_input("Habit name", placeholder="e.g., Exercise 30 min")
    if st.button("Save Habit"):
        if habit_name.strip():
            ok, msg = add_habit(habit_name.strip())
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")
        else:
            st.warning("Please enter a valid habit name.")
    st.divider()
    st.caption("Existing habits")
    habits_df = get_habits_df()
    if habits_df.empty:
        st.info("No habits yet.")
    else:
        st.dataframe(habits_df, use_container_width=True)

# Log Habit
elif menu == "Log Habit":
    st.subheader("📝 Log today's habit")
    habits_df = get_habits_df()
    if habits_df.empty:
        st.info("No habits found. Add a habit first.")
    else:
        habit = st.selectbox("Select habit", habits_df["name"].tolist())
        if st.button("Log Today"):
            ok, msg = log_habit(habit)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

# View Progress
elif menu == "View Progress":
    st.subheader("📊 Progress overview")
    df = get_progress_df()
    if df.empty:
        st.info("No data yet. Add and log habits to see progress.")
    else:
        # Text summary
        for _, row in df.iterrows():
            st.write(f"- **{row['habit']}**: {int(row['count'])} days completed")

        # Bar chart
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(df["habit"], df["count"], color="#2575fc")
        ax.set_xlabel("Habits", color="#203a43")
        ax.set_ylabel("Days Completed", color="#203a43")
        ax.set_title("Habit Progress", color="#6a11cb")
        plt.xticks(rotation=30, ha="right", color="#000000")
        plt.yticks(color="#000000")
        st.pyplot(fig)

st.caption("✨ Gradient theme applied everywhere.")

import os
import sqlite3
from models import db, app

DATABASE_PATH = "instance/database.db"
SQL_POPULATE_SCRIPT = "populate_db.sql" 

# delete existing db and then recreat it
def reset_database():
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    with app.app_context():
        db.create_all() # creates instance/database.db

# populate the database with fake data from populate_db.sql
def populate_database():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        with open(SQL_POPULATE_SCRIPT, "r") as f:
            sql_script = f.read()
            cursor.executescript(sql_script)
        conn.commit()

if __name__ == "__main__":
    reset_database()
    populate_database()
    print("Database created and populated")


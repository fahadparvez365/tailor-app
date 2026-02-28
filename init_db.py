import sqlite3

conn = sqlite3.connect('database.db')

conn.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_code TEXT,
    customer_name TEXT,
    phone TEXT,

    suits INTEGER,
    order_date TEXT,
    delivery_date TEXT,

    qameez_length REAL,
    bazo REAL,
    tera REAL,
    gala REAL,
    chest REAL,
    kamar REAL,
    shalwar REAL,
    poncha REAL,
    pajama REAL,

    gera TEXT,
    collar_type TEXT,
    silai TEXT,
    front_pocket TEXT,
    shalwar_pocket TEXT,
    button_type TEXT,

    total_amount REAL,
    advance_payment REAL,
    remaining_balance REAL,

    notes TEXT
)
""")

conn.commit()
conn.close()

print("DB Ready ✅")
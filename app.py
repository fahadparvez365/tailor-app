from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date, timedelta
import json

app = Flask(__name__)


# -----------------------------
# DATABASE - SQLite
# -----------------------------
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    return dict(row) if row else None

def fetch_val(row):
    return list(dict(row).values())[0]


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_code TEXT, customer_name TEXT, phone TEXT,
        suits INTEGER, order_date TEXT, delivery_date TEXT,
        qameez_length REAL, bazo REAL, tera REAL, gala REAL, chest REAL,
        kamar REAL, shalwar REAL, poncha REAL, pajama REAL,
        gera TEXT, collar_type TEXT, silai TEXT,
        front_pocket TEXT, shalwar_pocket TEXT, button_type TEXT,
        total_amount REAL, advance_payment REAL, remaining_balance REAL,
        notes TEXT
    )
    """)

    cur.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS custom_fields (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field_name TEXT, field_label TEXT,
        field_type TEXT DEFAULT 'number',
        is_active INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    )
    """)

    defaults = [
        ('shop_name', 'رباب ٹیلرز'),
        ('shop_address', 'بٹ چوک المدینہ مسجد کوٹلی آزاد کشمیر'),
        ('shop_phone', '03045952882'),
        ('username', 'admin'),
        ('password', '123'),
    ]
    for key, value in defaults:
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

    cur.execute("SELECT COUNT(*) as cnt FROM custom_fields")
    count = fetch_val(cur.fetchone()) or 0
    if count == 0:
        default_fields = [
            ('qameez_length', 'قمیض لمبائی', 'number', 1, 1),
            ('bazo', 'بازو', 'number', 1, 2),
            ('tera', 'تیرہ', 'number', 1, 3),
            ('gala', 'گلا', 'number', 1, 4),
            ('chest', 'چھاتی', 'number', 1, 5),
            ('kamar', 'کمر', 'number', 1, 6),
            ('shalwar', 'شلوار', 'number', 1, 7),
            ('poncha', 'پونچہ', 'number', 1, 8),
            ('pajama', 'پاجامہ', 'number', 1, 9),
        ]
        for f in default_fields:
            cur.execute(
                "INSERT INTO custom_fields (field_name, field_label, field_type, is_active, sort_order) VALUES (?,?,?,?,?)", f
            )

    conn.commit()
    cur.close()
    conn.close()


with app.app_context():
    init_db()


# -----------------------------
# LOGIN
# -----------------------------
@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key=?", ('username',))
    db_user = row_to_dict(cur.fetchone())
    cur.execute("SELECT value FROM settings WHERE key=?", ('password',))
    db_pass = row_to_dict(cur.fetchone())
    cur.close()
    conn.close()
    if username == db_user['value'] and password == db_pass['value']:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="❌ غلط صارف نام یا پاس ورڈ")


@app.route('/dashboard')
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) as cnt FROM customers")
    total_customers = fetch_val(cur.fetchone()) or 0
    cur.execute("SELECT SUM(total_amount) as s FROM customers")
    total_amount = fetch_val(cur.fetchone()) or 0
    cur.execute("SELECT COUNT(*) as cnt FROM customers WHERE remaining_balance > 0")
    pending = fetch_val(cur.fetchone()) or 0
    cur.execute("SELECT COUNT(*) as cnt FROM customers WHERE remaining_balance = 0 OR remaining_balance IS NULL")
    completed = fetch_val(cur.fetchone()) or 0
    cur.execute("SELECT * FROM customers ORDER BY id DESC LIMIT 5")
    recent = [row_to_dict(r) for r in cur.fetchall()]

    cur.close()
    conn.close()
    return render_template('dashboard.html',
        total_customers=total_customers,
        total_amount=total_amount,
        pending=pending,
        completed=completed,
        recent=recent
    )


# -----------------------------
# ADD CUSTOMER
# -----------------------------
@app.route('/add-customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO customers (
                customer_code, customer_name, phone,
                suits, order_date, delivery_date,
                qameez_length, bazo, tera, gala, chest,
                kamar, shalwar, poncha, pajama,
                gera, collar_type, silai,
                front_pocket, shalwar_pocket, button_type,
                total_amount, advance_payment, remaining_balance, notes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            request.form.get('customer_code'), request.form.get('customer_name'),
            request.form.get('phone'), request.form.get('suits'),
            request.form.get('order_date'), request.form.get('delivery_date'),
            request.form.get('qameez_length'), request.form.get('bazo'),
            request.form.get('tera'), request.form.get('gala'),
            request.form.get('chest'), request.form.get('kamar'),
            request.form.get('shalwar'), request.form.get('poncha'),
            request.form.get('pajama'), request.form.get('gera'),
            request.form.get('collar_type'), request.form.get('silai'),
            request.form.get('front_pocket'), request.form.get('shalwar_pocket'),
            request.form.get('button_type'), request.form.get('total_amount'),
            request.form.get('advance_payment'), request.form.get('remaining_balance'),
            request.form.get('notes')
        ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('add_customer', success='1'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT customer_code FROM customers ORDER BY id DESC LIMIT 1")
    last = row_to_dict(cur.fetchone())
    cur.execute("SELECT * FROM custom_fields WHERE is_active=1 ORDER BY sort_order")
    fields = [row_to_dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()

    if last and last.get('customer_code') and last['customer_code'].startswith('RB-'):
        num = int(last['customer_code'].split('-')[1]) + 1
        auto_id = f"RB-{num:04d}"
    else:
        auto_id = "RB-0001"

    return render_template('add-customer.html', auto_id=auto_id, success=request.args.get('success'), fields=fields)


@app.route('/view-customers')
def view_customers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers ORDER BY id DESC")
    customers = [row_to_dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template('view-customer.html', customers=customers)


@app.route('/delete-customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {'success': True}


@app.route('/update-customer')
def update_customer():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM custom_fields WHERE is_active=1 ORDER BY sort_order")
    fields = [row_to_dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template('update-customer.html', fields=fields, success=request.args.get('success'))


@app.route('/search-customer')
def search_customer():
    query = request.args.get('q', '')
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, customer_name, phone, customer_code FROM customers WHERE customer_name LIKE ? OR phone LIKE ?",
        (f'%{query}%', f'%{query}%')
    )
    customers = [row_to_dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {'customers': customers}


@app.route('/get-customer/<int:customer_id>')
def get_customer(customer_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    c = row_to_dict(cur.fetchone())
    cur.close()
    conn.close()
    return c


@app.route('/update-customer/<int:customer_id>', methods=['POST'])
def update_customer_save(customer_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE customers SET
            customer_name=?, phone=?, suits=?,
            order_date=?, delivery_date=?,
            qameez_length=?, bazo=?, tera=?, gala=?, chest=?,
            kamar=?, shalwar=?, poncha=?, pajama=?,
            gera=?, collar_type=?, silai=?,
            front_pocket=?, shalwar_pocket=?, button_type=?,
            total_amount=?, advance_payment=?, remaining_balance=?, notes=?
        WHERE id=?
    """, (
        request.form.get('customer_name'), request.form.get('phone'),
        request.form.get('suits'), request.form.get('order_date'),
        request.form.get('delivery_date'), request.form.get('qameez_length'),
        request.form.get('bazo'), request.form.get('tera'),
        request.form.get('gala'), request.form.get('chest'),
        request.form.get('kamar'), request.form.get('shalwar'),
        request.form.get('poncha'), request.form.get('pajama'),
        request.form.get('gera'), request.form.get('collar_type'),
        request.form.get('silai'), request.form.get('front_pocket'),
        request.form.get('shalwar_pocket'), request.form.get('button_type'),
        request.form.get('total_amount'), request.form.get('advance_payment'),
        request.form.get('remaining_balance'), request.form.get('notes'),
        customer_id
    ))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('update_customer', success='1'))


@app.route('/receipt')
def receipt():
    return render_template('receipt.html')


@app.route('/reports')
def reports():
    conn = get_db()
    cur = conn.cursor()
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    week_start = (date.today() - timedelta(days=7)).isoformat()
    month_start = date.today().replace(day=1).isoformat()

    def fetch_one(sql, params=()):
        cur.execute(sql, params)
        return fetch_val(cur.fetchone()) or 0

    def fetch_all(sql, params=()):
        cur.execute(sql, params)
        return [row_to_dict(r) for r in cur.fetchall()]

    today_customers = fetch_all("SELECT * FROM customers WHERE order_date=? ORDER BY id DESC", (today,))
    today_income = fetch_one("SELECT SUM(total_amount) as s FROM customers WHERE order_date=?", (today,))
    today_advance = fetch_one("SELECT SUM(advance_payment) as s FROM customers WHERE order_date=?", (today,))
    week_income = fetch_one("SELECT SUM(total_amount) as s FROM customers WHERE order_date>=?", (week_start,))
    month_income = fetch_one("SELECT SUM(total_amount) as s FROM customers WHERE order_date>=?", (month_start,))
    total_income = fetch_one("SELECT SUM(total_amount) as s FROM customers")
    total_advance = fetch_one("SELECT SUM(advance_payment) as s FROM customers")
    total_pending = fetch_one("SELECT SUM(remaining_balance) as s FROM customers WHERE remaining_balance>0")
    pending_customers = fetch_all("SELECT * FROM customers WHERE remaining_balance>0 ORDER BY delivery_date ASC")
    today_delivery = fetch_all("SELECT * FROM customers WHERE delivery_date=? ORDER BY id DESC", (today,))
    tomorrow_delivery = fetch_all("SELECT * FROM customers WHERE delivery_date=? ORDER BY id DESC", (tomorrow,))

    daily_labels, daily_income_list, daily_customers = [], [], []
    for i in range(6, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        label = (date.today() - timedelta(days=i)).strftime('%d/%m')
        income = fetch_one("SELECT SUM(total_amount) as s FROM customers WHERE order_date=?", (d,))
        count = fetch_one("SELECT COUNT(*) as cnt FROM customers WHERE order_date=?", (d,))
        daily_labels.append(label)
        daily_income_list.append(float(income))
        daily_customers.append(int(count))

    monthly_labels, monthly_income_list, monthly_customers_data = [], [], []
    for i in range(5, -1, -1):
        d = date.today().replace(day=1) - timedelta(days=i*28)
        m_start = d.replace(day=1).isoformat()
        m_end = d.replace(month=d.month+1, day=1).isoformat() if d.month < 12 else d.replace(year=d.year+1, month=1, day=1).isoformat()
        label = d.strftime('%b %Y')
        income = fetch_one("SELECT SUM(total_amount) as s FROM customers WHERE order_date>=? AND order_date<?", (m_start, m_end))
        count = fetch_one("SELECT COUNT(*) as cnt FROM customers WHERE order_date>=? AND order_date<?", (m_start, m_end))
        monthly_labels.append(label)
        monthly_income_list.append(float(income))
        monthly_customers_data.append(int(count))

    cur.close()
    conn.close()

    return render_template('reports.html',
        today=today,
        today_customers=today_customers,
        today_income=today_income,
        today_advance=today_advance,
        week_income=week_income,
        month_income=month_income,
        total_income=total_income,
        total_advance=total_advance,
        total_pending=total_pending,
        pending_customers=pending_customers,
        today_delivery=today_delivery,
        tomorrow_delivery=tomorrow_delivery,
        daily_labels=json.dumps(daily_labels),
        daily_income=json.dumps(daily_income_list),
        daily_customers=json.dumps(daily_customers),
        monthly_labels=json.dumps(monthly_labels),
        monthly_income=json.dumps(monthly_income_list),
        monthly_customers_data=json.dumps(monthly_customers_data),
    )


@app.route('/settings')
def settings():
    conn = get_db()
    cur = conn.cursor()

    def get_setting(key):
        cur.execute("SELECT value FROM settings WHERE key=?", (key,))
        return row_to_dict(cur.fetchone())['value']

    shop_name = get_setting('shop_name')
    shop_address = get_setting('shop_address')
    shop_phone = get_setting('shop_phone')
    username = get_setting('username')

    cur.execute("SELECT * FROM custom_fields ORDER BY sort_order")
    fields = [row_to_dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template('Settings.html',
        shop_name=shop_name,
        shop_address=shop_address,
        shop_phone=shop_phone,
        username=username,
        fields=fields,
        success=request.args.get('success')
    )


@app.route('/settings/shop', methods=['POST'])
def settings_shop():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET value=? WHERE key=?", (request.form.get('shop_name'), 'shop_name'))
    cur.execute("UPDATE settings SET value=? WHERE key=?", (request.form.get('shop_address'), 'shop_address'))
    cur.execute("UPDATE settings SET value=? WHERE key=?", (request.form.get('shop_phone'), 'shop_phone'))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('settings', success='shop'))


@app.route('/settings/login', methods=['POST'])
def settings_login():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET value=? WHERE key=?", (request.form.get('username'), 'username'))
    new_pass = request.form.get('new_password')
    if new_pass:
        cur.execute("UPDATE settings SET value=? WHERE key=?", (new_pass, 'password'))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('settings', success='login'))


@app.route('/settings/field/add', methods=['POST'])
def settings_field_add():
    field_label = request.form.get('field_label')
    field_name = field_label.replace(' ', '_').lower() + '_custom'
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT MAX(sort_order) as mx FROM custom_fields")
    max_order = fetch_val(cur.fetchone()) or 0
    cur.execute(
        "INSERT INTO custom_fields (field_name, field_label, field_type, is_active, sort_order) VALUES (?,?,'number',1,?)",
        (field_name, field_label, max_order + 1)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('settings', success='field'))


@app.route('/settings/field/delete/<int:field_id>', methods=['POST'])
def settings_field_delete(field_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM custom_fields WHERE id=?", (field_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {'success': True}


@app.route('/settings/field/toggle/<int:field_id>', methods=['POST'])
def settings_field_toggle(field_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE custom_fields SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE id=?", (field_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {'success': True}


@app.route('/settings/field/rename/<int:field_id>', methods=['POST'])
def settings_field_rename(field_id):
    new_label = request.form.get('field_label')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE custom_fields SET field_label=? WHERE id=?", (new_label, field_id))
    conn.commit()
    cur.close()
    conn.close()
    return {'success': True}


@app.route('/get-fields')
def get_fields():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM custom_fields WHERE is_active=1 ORDER BY sort_order")
    fields = [row_to_dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {'fields': fields}


@app.route('/settings/field/reorder', methods=['POST'])
def settings_field_reorder():
    orders = request.json.get('orders', [])
    conn = get_db()
    cur = conn.cursor()
    for item in orders:
        cur.execute("UPDATE custom_fields SET sort_order=? WHERE id=?", (item['order'], item['id']))
    conn.commit()
    cur.close()
    conn.close()
    return {'success': True}


# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
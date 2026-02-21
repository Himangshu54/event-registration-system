from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"

# 🔹 MySQL Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tuktuk*2006",
        database="event_db"
    )

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/register-page')
def register_page():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO registrations (name, email, phone) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, email, phone))
    conn.commit()

    cursor.close()
    conn.close()

    return render_template('success.html', name=name, email=email, phone=phone)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )

        admin = cursor.fetchone()

        cursor.close()
        conn.close()

        if admin:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            return "Invalid Credentials"

    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    search_query = request.form.get('search')

    if search_query:
        cursor.execute(
            "SELECT * FROM registrations WHERE name LIKE %s",
            ('%' + search_query + '%',)
        )
    else:
        cursor.execute("SELECT * FROM registrations")

    data = cursor.fetchall()

    # 🔹 Count total registrations
    cursor.execute("SELECT COUNT(*) FROM registrations")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        'admin.html',
        registrations=data,
        total_registrations=total
    )

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/login')

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin_logged_in'):
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM registrations WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/admin')

@app.route('/test')
def test():
    return "Flask is working"

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('admin_logged_in'):
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cursor.execute("""
            UPDATE registrations
            SET name=%s, email=%s, phone=%s
            WHERE id=%s
        """, (name, email, phone, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/admin')

    cursor.execute("SELECT * FROM registrations WHERE id=%s", (id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('edit.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
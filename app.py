import sqlite3
from flask import Flask, request, g, redirect, url_for, render_template_string, render_template, session

# We configure Flask to serve static files from the current directory
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.secret_key = 'super_secret_health_key'

DATABASE = 'visits.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database and create the visitors and bookings tables."""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                user_agent TEXT,
                path TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                email TEXT,
                booking_date TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# Initialize DB when the app starts
init_db()



@app.route('/')
def index():
    """Serve the main index.html file for the root path."""
    return app.send_static_file('Index.html')

@app.route('/book', methods=['POST'])
def book_appointment():
    """Handle the booking form submission."""
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    booking_date = request.form.get('booking_date')
    
    if full_name and email and booking_date:
        db = get_db()
        db.execute(
            'INSERT INTO bookings (full_name, email, booking_date) VALUES (?, ?, ?)',
            [full_name, email, booking_date]
        )
        db.commit()
    
    # Redirect back to home page after booking
    return redirect(url_for('index', success='true'))

@app.route('/admin')
def admin():
    """A simple admin interface to view booking logs."""
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    db = get_db()
    
    # Get bookings
    cur2 = db.execute('SELECT * FROM bookings ORDER BY timestamp DESC LIMIT 100')
    bookings = cur2.fetchall()
    
    return render_template('admin.html', bookings=bookings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'Saksham0012' and password == 'Saksham@2006':
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login', error='1'))
    return app.send_static_file('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/api/auth_status')
def auth_status():
    from flask import jsonify
    return jsonify({"is_admin": session.get('is_admin', False)})

@app.route('/reset', methods=['POST'])
def reset():
    """Endpoint required by OpenEnv to reset the environment."""
    return {"status": "ok", "message": "Environment reset successful"}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

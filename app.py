from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import sqlite3

app = Flask(__name__)
CORS(app, origins=["https://finley-davis.github.io"])  # Adjust origin as needed

DATABASE = 'data.db'

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
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ph REAL,
                do REAL,
                conductivity REAL,
                airTemp REAL,
                waterTemp REAL,
                observations TEXT
            )
        ''')
        db.commit()

@app.route('/')
def index():
    return "✅ Longhorn Stream Team backend is running!"

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO submissions (ph, do, conductivity, airTemp, waterTemp, observations)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        float(data.get('ph', 0)),
        float(data.get('do', 0)),
        float(data.get('conductivity', 0)),
        float(data.get('airTemp', 0)),
        float(data.get('waterTemp', 0)),
        data.get('observations', '')
    ))
    db.commit()

    return jsonify({'message': '✅ Data submitted successfully!'})

@app.route('/get_data', methods=['GET'])
def get_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT ph, do, conductivity, airTemp, waterTemp, observations FROM submissions')
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(results)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

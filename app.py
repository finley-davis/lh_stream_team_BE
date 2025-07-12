from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://finley-davis.github.io"])

DB_FILE = 'data.db'

# Initialize the database and create table if it doesn't exist
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stream TEXT NOT NULL,
                date TEXT NOT NULL,
                ph REAL,
                do REAL,
                conductivity REAL,
                airTemp REAL,
                waterTemp REAL,
                observations TEXT
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def index():
    return "✅ Longhorn Stream Team backend is running!"

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    stream = data.get('stream')
    if not stream:
        return jsonify({'error': 'Stream name is required'}), 400

    # Use provided date or current time ISO8601 string
    date = data.get('date', datetime.utcnow().isoformat())

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO submissions (stream, date, ph, do, conductivity, airTemp, waterTemp, observations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stream,
            date,
            float(data.get('ph', 0)),
            float(data.get('do', 0)),
            float(data.get('conductivity', 0)),
            float(data.get('airTemp', 0)),
            float(data.get('waterTemp', 0)),
            data.get('observations', '')
        ))
        conn.commit()

    return jsonify({'message': '✅ Data submitted successfully!'})

@app.route('/get_data', methods=['GET'])
def get_data():
    stream = request.args.get('stream')
    if not stream:
        return jsonify({'error': 'Stream parameter is required'}), 400

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT date, ph, do, conductivity, airTemp, waterTemp, observations
            FROM submissions WHERE stream = ? ORDER BY date ASC
        ''', (stream,))
        rows = c.fetchall()
        data = [{
            'date': row[0],
            'ph': row[1],
            'do': row[2],
            'conductivity': row[3],
            'airTemp': row[4],
            'waterTemp': row[5],
            'observations': row[6]
        } for row in rows]
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

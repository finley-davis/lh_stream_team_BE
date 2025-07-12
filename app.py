from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os

app = Flask(__name__)

# Enable CORS for your frontend origin, or for testing allow all origins:
CORS(app, origins=["https://finley-davis.github.io"])  # or CORS(app) to allow all

DATA_FILE = 'submissions.csv'

@app.route('/')
def index():
    return "✅ Longhorn Stream Team backend is running!"

@app.route('/submit', methods=['POST', 'OPTIONS'])
def submit():
    if request.method == 'OPTIONS':
        # Allows preflight requests to pass
        response = app.make_default_options_response()
        return response

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    # Append to CSV
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

    return jsonify({'message': '✅ Data submitted successfully!'})

@app.route('/get_data', methods=['GET'])
def get_data():
    if not os.path.isfile(DATA_FILE):
        return jsonify([])

    with open(DATA_FILE, newline='') as f:
        reader = csv.DictReader(f)
        return jsonify(list(reader))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
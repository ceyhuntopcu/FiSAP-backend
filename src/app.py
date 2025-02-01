from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from werkzeug.utils import secure_filename
from resource_allocation import deploy_resources
from report_generation import generate_report
from data_processing import load_wildfire_data

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
CORS(app)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = f"{UPLOAD_FOLDER}/{filename}"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(file_path)

    wildfire_data = load_wildfire_data(file_path)
    wildfire_data["timestamp"] = pd.to_datetime(wildfire_data["timestamp"])
    wildfire_data["fire_start_time"] = pd.to_datetime(wildfire_data["fire_start_time"])
    wildfire_data = wildfire_data.sort_values(by=["fire_start_time", "severity"], ascending=[True, False])

    fires_addressed, missed_responses, operational_cost, total_damage_cost, allocations = deploy_resources(
        wildfire_data)
    report = generate_report(fires_addressed, missed_responses, operational_cost, total_damage_cost)

    return jsonify({"message": "File processed successfully!", "report": report})


if __name__ == '__main__':
    app.run(debug=True)
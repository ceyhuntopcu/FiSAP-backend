from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from resource_allocation import deploy_resources
from report_generation import generate_report

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
CSV_FILE_PATH = os.path.join(UPLOAD_FOLDER, "current_wildfiredata.csv")

global_deployment_records = []

@app.route('/upload', methods=['POST'])
def upload_csv():
    global global_deployment_records

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400  # Ensure file is uploaded

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    wildfire_data = pd.read_csv(file_path)
    wildfire_data["timestamp"] = pd.to_datetime(wildfire_data["timestamp"])
    wildfire_data["fire_start_time"] = pd.to_datetime(wildfire_data["fire_start_time"])
    wildfire_data = wildfire_data.sort_values(by=["fire_start_time", "severity"], ascending=[True, False])

    fires_addressed, missed_responses, operational_cost, total_damage_cost, deployment_records, severity_count = deploy_resources(
        wildfire_data)

    global_deployment_records = deployment_records.copy()
    print(f"🔥 Successfully saved {len(global_deployment_records)} deployments to global variable.")

    report = generate_report(fires_addressed, missed_responses, operational_cost, total_damage_cost, severity_count)
    return jsonify({"message": "File processed successfully!", "report": report})

@app.route('/deployments', methods=['GET'])
def get_deployments():
    return jsonify({"deployments": global_deployment_records})

@app.route('/update_severity', methods=['PUT'])
def update_severity():
    data = request.get_json()

    location = data.get('location')
    new_severity = data.get('severity')

    if not location or not new_severity:
        return jsonify({"error": "Missing location or severity"}), 400

    if not os.path.exists(CSV_FILE_PATH):
        return jsonify({"error": "CSV file not found"}), 500

    df = pd.read_csv(CSV_FILE_PATH)

    mask = df["location"] == location
    if mask.sum() == 0:
        return jsonify({"error": "No wildfire found at the given location"}), 404

    df.loc[mask, "severity"] = new_severity
    df.to_csv(CSV_FILE_PATH, index=False)

    updated_fire = df.loc[mask].to_dict(orient="records")[0]

    return jsonify({
        "message": "Severity updated successfully!",
        "updated_fire": updated_fire
    })

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from resource_allocation import deploy_resources
from report_generation import generate_report
from datetime import timedelta
from model import predict

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
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    wildfire_data = pd.read_csv(file_path)
    wildfire_data["timestamp"] = pd.to_datetime(wildfire_data["timestamp"])
    wildfire_data["fire_start_time"] = pd.to_datetime(wildfire_data["fire_start_time"])
    wildfire_data = wildfire_data.sort_values(by=["fire_start_time", "severity"], ascending=[True, False])

    resources = {
        "Smoke Jumpers": {"deployment_time": timedelta(minutes=30), "cost": 5000, "availability": 5},
        "Fire Engines": {"deployment_time": timedelta(hours=1), "cost": 2000, "availability": 10},
        "Helicopters": {"deployment_time": timedelta(minutes=45), "cost": 8000, "availability": 3},
        "Tanker Planes": {"deployment_time": timedelta(hours=2), "cost": 15000, "availability": 2},
        "Ground Crews": {"deployment_time": timedelta(hours=1.5), "cost": 3000, "availability": 8},
    }

    fires_addressed, missed_responses, operational_cost, total_damage_cost, deployment_records, severity_count = deploy_resources(
        wildfire_data, resources)

    global_deployment_records = deployment_records.copy()
    print(f"🔥 Successfully saved {len(global_deployment_records)} deployments to global variable.")

    report = generate_report(fires_addressed, missed_responses, operational_cost, total_damage_cost, severity_count)
    return jsonify({"message": "File processed successfully!", "data": report})

@app.route('/deployments', methods=['GET'])
def get_deployments():
    return jsonify({"data": global_deployment_records})

# @app.route('/get_resources', methods=['GET'])
# def get_resources():
#     resources = get_current_resources()
#     return jsonify({"resources": resources})

@app.route('/predictions', methods=['POST'])
def get_predictions():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    df = pd.read_csv(file_path)
    result_df = predict(df.copy())

    # Convert timestamp to datetime and extract date
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date

    # Group by date and aggregate locations (joining multiple locations into a list)
    df["location"] = df["latitude"].astype(str) + ", " + df["longitude"].astype(str)
    grouped_df = df.groupby("date")["location"].first().reset_index()
    result_df["location"] = grouped_df["location"]

    return jsonify({"data": result_df.to_dict('records')})


if __name__ == '__main__':
    app.run(debug=True)

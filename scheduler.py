import csv

import pandas as pd
from datetime import datetime, timedelta

# Load wildfire data
file_path = "csv_files/current_wildfiredata.csv"
wildfire_data = pd.read_csv(file_path)

# Convert timestamps to datetime format
wildfire_data["timestamp"] = pd.to_datetime(wildfire_data["timestamp"])
wildfire_data["fire_start_time"] = pd.to_datetime(wildfire_data["fire_start_time"])

# Define firefighting resources
resources = {
    "Smoke Jumpers": {"deployment_time": timedelta(minutes=30), "cost": 5000, "availability": 5},
    "Fire Engines": {"deployment_time": timedelta(hours=1), "cost": 2000, "availability": 10},
    "Helicopters": {"deployment_time": timedelta(minutes=45), "cost": 8000, "availability": 3},
    "Tanker Planes": {"deployment_time": timedelta(hours=2), "cost": 15000, "availability": 2},
    "Ground Crews": {"deployment_time": timedelta(hours=1.5), "cost": 3000, "availability": 8},
}

# Define damage costs for missed responses
damage_costs = {
    "low": 50000,
    "medium": 100000,
    "high": 200000,
}

# Sort wildfires by severity (high to low) and then by fire_start_time
wildfire_data = wildfire_data.sort_values(by=["fire_start_time", "severity"], ascending=[True, False])

# Track ongoing deployments and their completion times
ongoing_deployments = []

# Reset available resources
available_resources = {key: val["availability"] for key, val in resources.items()}

# Reset tracking variables
missed_responses = {"low": 0, "medium": 0, "high": 0}
allocations = []
operational_cost = 0
total_damage_cost = 0
fires_addressed = 0

# Process wildfires in order of severity and start time
for _, fire in wildfire_data.iterrows():
    fire_severity = fire["severity"].lower()
    fire_start = fire["fire_start_time"]

    print(f"{fire_severity=} {fire_start=}")

    # Release resources that have completed their deployment
    ongoing_deployments = [d for d in ongoing_deployments if d["end_time"] > fire_start]
    print(f"{ongoing_deployments=}")

    # Update available resources
    for deployment in ongoing_deployments:
        available_resources[deployment["resource"]] += 1

    resources_used = None

    # Assign the best available resource
    for resource, details in resources.items():
        if available_resources[resource] > 0:
            deployment_end = fire_start + details["deployment_time"]
            ongoing_deployments.append({"resource": resource, "end_time": deployment_end})
            available_resources[resource] -= 1
            operational_cost += details["cost"]
            fires_addressed += 1
            resources_used = resource

            allocations.append([fire_start, resources_used, operational_cost])

            break  # Assign the first available resource

    if not resources_used:
        missed_responses[fire_severity] += 1
        total_damage_cost += damage_costs[fire_severity]

# Generate updated report
updated_report = {
    "Fires Addressed": fires_addressed,
    "Fires Missed (Low)": missed_responses["low"],
    "Fires Missed (Medium)": missed_responses["medium"],
    "Fires Missed (High)": missed_responses["high"],
    "Total Operational Cost": operational_cost,
    "Total Damage Cost": total_damage_cost,
}
print(updated_report)

# Write allocations to csv
file_path = "current_report.csv"
csv.writer(open(file_path, "w")).writerows(allocations)
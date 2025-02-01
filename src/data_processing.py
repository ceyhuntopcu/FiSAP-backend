import pandas as pd

def load_wildfire_data(file_path):
    wildfire_data = pd.read_csv(file_path)

    wildfire_data["timestamp"] = pd.to_datetime(wildfire_data["timestamp"])
    wildfire_data["fire_start_time"] = pd.to_datetime(wildfire_data["fire_start_time"])

    wildfire_data = wildfire_data.sort_values(by=["fire_start_time", "severity"], ascending=[True, False])

    return wildfire_data

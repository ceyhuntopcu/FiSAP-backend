import pandas as pd
from config import DATA_FILE

def load_wildfire_data():
    wildfire_data = pd.read_csv(DATA_FILE)

    wildfire_data["timestamp"] = pd.to_datetime(wildfire_data["timestamp"])
    wildfire_data["fire_start_time"] = pd.to_datetime(wildfire_data["fire_start_time"])

    wildfire_data = wildfire_data.sort_values(by=["fire_start_time", "severity"], ascending=[True, False])

    return wildfire_data

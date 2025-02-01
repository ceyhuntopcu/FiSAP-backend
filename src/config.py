from datetime import timedelta

RESOURCES = {
    "Smoke Jumpers": {"deployment_time": timedelta(minutes=30), "cost": 5000, "availability": 5},
    "Fire Engines": {"deployment_time": timedelta(hours=1), "cost": 2000, "availability": 10},
    "Helicopters": {"deployment_time": timedelta(minutes=45), "cost": 8000, "availability": 3},
    "Tanker Planes": {"deployment_time": timedelta(hours=2), "cost": 15000, "availability": 2},
    "Ground Crews": {"deployment_time": timedelta(hours=1.5), "cost": 3000, "availability": 8},
}

DAMAGE_COSTS = {
    "low": 50000,
    "medium": 100000,
    "high": 200000,
}

REPORT_FILE = "report/current_report.txt"

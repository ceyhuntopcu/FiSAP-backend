from config import RESOURCES, DAMAGE_COSTS
from collections import defaultdict

def deploy_resources(wildfire_data):
    global deployment_records
    deployment_records = []

    ongoing_deployments = []
    available_resources = {key: val["availability"] for key, val in RESOURCES.items()}

    missed_responses = {"low": 0, "medium": 0, "high": 0}
    severity_count = defaultdict(int)

    operational_cost = 0
    total_damage_cost = 0
    fires_addressed = 0

    for _, fire in wildfire_data.iterrows():
        fire_severity = fire["severity"].lower()
        fire_start = fire["fire_start_time"]
        location = fire.get("location", "Unknown Location")

        severity_count[fire_severity] += 1

        ongoing_deployments = [d for d in ongoing_deployments if d["end_time"] > fire_start]

        for deployment in ongoing_deployments:
            available_resources[deployment["resource"]] += 1

        resources_used = None

        curr_fire = {
            "fire_start_time": fire_start.strftime("%Y-%m-%d %H:%M:%S"),
            "location": location,
            "severity": fire_severity,
            "is_deployed": False,
            "resource_used": None
        }

        for resource, details in RESOURCES.items():
            if available_resources[resource] > 0:
                deployment_end = fire_start + details["deployment_time"]
                ongoing_deployments.append({"resource": resource, "end_time": deployment_end})
                available_resources[resource] -= 1
                operational_cost += details["cost"]
                fires_addressed += 1
                resources_used = resource

                curr_fire["is_deployed"] = True
                curr_fire["resource_used"] = resource

                break

        deployment_records.append(curr_fire)
        print(f"✅ Deployment added: {deployment_records[-1]}")

        if not resources_used:
            missed_responses[fire_severity] += 1
            total_damage_cost += DAMAGE_COSTS[fire_severity]

    return fires_addressed, missed_responses, operational_cost, total_damage_cost, deployment_records, severity_count


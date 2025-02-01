from data_processing import load_wildfire_data
from resource_allocation import deploy_resources
from report_generation import generate_report

if __name__ == "__main__":
    print("🔥 Loading wildfire data...")
    wildfire_data = load_wildfire_data()

    print("🚒 Deploying firefighting resources...")
    fires_addressed, missed_responses, operational_cost, total_damage_cost, allocations = deploy_resources(wildfire_data)

    print("📊 Generating report...")
    report = generate_report(fires_addressed, missed_responses, operational_cost, total_damage_cost)

    print("✅ Process completed!")

from config import REPORT_FILE


def generate_report(fires_addressed, missed_responses, operational_cost, total_damage_cost):
    total_missed = sum(missed_responses.values())
    severity_report = {
        "low": missed_responses["low"],
        "medium": missed_responses["medium"],
        "high": missed_responses["high"]
    }

    report_text = f"""
    Number of fires addressed: {fires_addressed}
    Number of fires delayed: {total_missed}
    Total operational costs: ${operational_cost}
    Estimated damage costs from delayed responses: ${total_damage_cost}
    Fire severity report: {severity_report}
    """

    with open(REPORT_FILE, "w", newline='') as f:
        f.write(report_text.strip())
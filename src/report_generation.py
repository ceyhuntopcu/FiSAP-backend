from config import REPORT_FILE

def generate_report(fires_addressed, missed_responses, operational_cost, total_damage_cost, severity_count):
    total_missed = sum(missed_responses.values())

    report_text = f"""
    Number of fires addressed: {fires_addressed}
    Number of fires delayed: {total_missed}
    Total operational costs: ${operational_cost}
    Estimated damage costs from delayed responses: ${total_damage_cost}
    Fire severity report: {severity_count}
    """

    with open(REPORT_FILE, "w", newline='') as f:
        f.write(report_text.strip())

    return {
        "Number of fires addressed": fires_addressed,
        "Number of fires delayed": total_missed,
        "Total operational costs": f"${operational_cost}",
        "Estimated damage costs from delayed responses": f"${total_damage_cost}",
        "Fire severity report": severity_count
    }

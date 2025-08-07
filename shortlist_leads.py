from copy import deepcopy
import json
from datetime import datetime
from utils.config_loader import TABLES
from utils.airtable_operations import fetch_records_from_table, sanitize_records, upsert_records


TIER_1_COMPANIES = {
    "Google", "Meta", "OpenAI", "Amazon", "Microsoft", "Netflix",
    "Apple", "Tesla", "Uber", "Airbnb", "Stripe", "Salesforce", "LinkedIn"
}
ALLOWED_LOCATIONS = {"US", "Canada", "UK", "Germany", "India"}


def verify_shortlist_criteria(applicant_id, compressed_json):
    """
    Verify if the applicant meets the shortlist criteria.
    """
    # Experience check
    work_experiences = compressed_json.get("experience", [])
    salary_preferences = compressed_json.get("salary", {})
    personal_details = compressed_json.get("personal", {})

    if not work_experiences or not salary_preferences or not personal_details:
        return False, "Missing required fields"

    # Initialize criteria
    meets_experience_criteria = False
    meets_compensation_criteria = False
    meets_location_criteria = False

    # Verify if applicant meets experience criteria
    total_years = 0
    is_from_tier1 = False
    has_4_yoe = False
    for experience in work_experiences:
        start = experience["start"]
        end = experience["end"]
        company = experience["company"]

        if company.lower() in {company.lower() for company in TIER_1_COMPANIES}:
            is_from_tier1 = True

        try:
            delta = (datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days
            total_years += delta / 365.0
            if total_years >= 4:
                has_4_yoe = True
        except Exception:
            continue

    # Convert currency to USD
    currency = salary_preferences.get("currency", "")
    if currency == "EUR":
        rate_in_usd = salary_preferences["rate"] * 1.15
        min_rate_in_usd = salary_preferences["min_rate"] * 1.15
    elif currency == "GBP":
        rate_in_usd = salary_preferences["rate"] * 1.3
        min_rate_in_usd = salary_preferences["min_rate"] * 1.3
    elif currency == "INR":
        rate_in_usd = salary_preferences["rate"] * 0.012
        min_rate_in_usd = salary_preferences["min_rate"] * 0.012

    # Verify if applicant meets all criteria
    meets_experience_criteria = is_from_tier1 or has_4_yoe
    meets_compensation_criteria = int(rate_in_usd) <= 100 and int(salary_preferences.get("availability", 0)) >= 20
    meets_location_criteria = personal_details.get("location", "").lower() in {location.lower() for location in ALLOWED_LOCATIONS}

    if meets_experience_criteria and meets_compensation_criteria and meets_location_criteria:
        if is_from_tier1:
            score_reason = f"""
            Worked at Tier-1 company with total experience of {total_years:.1f} years. 
            Expects compensation of {rate_in_usd} USD with availability of {salary_preferences.get('availability', 0)} hours per week.
            Currently in {personal_details.get('location', '')}.
            """
            return True, score_reason
        else:
            score_reason = f"""
            Worked at multiple companies having total experience of {total_years:.1f} years. 
            Expects compensation of {rate_in_usd} USD with availability of {salary_preferences.get('availability', 0)} hours per week. 
            Currently in {personal_details.get('location', '')}. 
            """
        return True, score_reason
    else:
        return False, "Does not meet all criteria"


def create_shortlisted_lead_record(applicant_id, compressed_json, score_reason, applicant_record_id):
    """
    Create a shortlisted lead record.
    """
    updated_shortlisted_lead_record = {
        "fields": {
            "Applicant": [
                applicant_record_id
            ],
            "Applicant ID": applicant_id,
            "Score Reason": score_reason,
            "Compressed JSON": compressed_json,
        }
    }
    return updated_shortlisted_lead_record


def main():
    """
    Shortlist leads.
    """
    final_shortlisted_leads = []
    final_applicants_records = []

    # Process applicants records to get shortlisted leads and update applicants records
    applicants_records = fetch_records_from_table(TABLES["applicants"])
    for i, applicant_record in enumerate(applicants_records):
        print(f"Processing applicant {i+1} of {len(applicants_records)}: {applicant_record['fields']['Applicant ID']}")

        applicant_fields = applicant_record.get("fields", {})
        applicant_id = applicant_fields["Applicant ID"]
        compressed_json = applicant_fields["Compressed JSON"]
        shortlist_status = applicant_fields["Shortlist Status"]

        if not compressed_json or not applicant_id:
            print(f"Skipping {applicant_id} because it doesn't have applicant ID or compressed JSON")
            continue

        if shortlist_status not in ["Waiting", "Invalid"]:
            print(f"Skipping {applicant_id} because it's already processed. Shortlist Status: {shortlist_status}")
            continue

        try:
            compressed_json_data = json.loads(compressed_json)
        except Exception as ex:
            print(f"Skipping invalid JSON for {applicant_id}: {ex}")
            continue

        is_shortlisted, reason = verify_shortlist_criteria(applicant_id, compressed_json_data)
        if is_shortlisted:
            updated_shortlisted_lead_record = create_shortlisted_lead_record(
                applicant_id=applicant_id,
                compressed_json=compressed_json,
                score_reason=reason,
                applicant_record_id=applicant_record["id"]
            )
            final_shortlisted_leads.append(updated_shortlisted_lead_record)

            # Create a new applicant record with shortlist status as "Processing"
            updated_applicant_record = deepcopy(applicant_record)
            updated_applicant_record["fields"]["Shortlist Status"] = "Processing"
            final_applicants_records.append(updated_applicant_record)

        else:
            # Create a new applicant record with shortlist status as "Rejected" or "Invalid"
            updated_applicant_record = deepcopy(applicant_record)
            if "missing" in reason.lower():
                updated_applicant_record["fields"]["Shortlist Status"] = "Invalid"
            else:
                updated_applicant_record["fields"]["Shortlist Status"] = "Rejected"
            final_applicants_records.append(updated_applicant_record)

        print(f"Applicant {applicant_id} Shortlist status: {updated_applicant_record['fields']['Shortlist Status']}")

    # Upsert final shortlisted leads
    i = 0
    while i < len(final_shortlisted_leads):
        j = min(i + 10, len(final_shortlisted_leads))
        print(f"Upserting {len(final_shortlisted_leads[i:j])} shortlisted leads in batch from index {i} to {j}")
        upsert_records(
            table_id=TABLES["shortlisted"],
            table_name="Shortlisted Leads",
            sanitized_records=final_shortlisted_leads[i:j],
            use_post=True
        )
        i = j

    # Upsert final applicants records
    sanitized_applicants_records = sanitize_records(final_applicants_records)
    i = 0
    while i < len(sanitized_applicants_records):
        j = min(i + 10, len(sanitized_applicants_records))
        print(f"Upserting {len(sanitized_applicants_records[i:j])} applicants records in batch from index {i} to {j}")
        upsert_records(
            table_id=TABLES["applicants"],
            table_name="Applicants",
            sanitized_records=sanitized_applicants_records[i:j],
            use_post=False
        )
        i = j

    print("Shortlist leads and update applicants records completed successfully!!!")


if __name__ == "__main__":
    main()

import requests
import json
import os
from copy import deepcopy
from utils.config_loader import HEADERS, AIRTABLE_BASE_ID, TABLES   


def fetch_records_from_table(table_id):
    """
    Fetch all records from a given table.
    """
    try:
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_id}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        return data.get("records", [])

    except Exception as ex:
        print(f"Error fetching records from {table_id}: {ex}")
        return []


def build_compressed_json(applicant_record, experience_records, personal_records, salary_records):
    """
    Build a compressed JSON object from the records.
    """
    applicant_id = applicant_record["fields"]["Applicant ID"]

    personal_data = {}
    for personal_record in personal_records:
        if personal_record.get("fields", {}).get("Applicant") is not None and applicant_id == personal_record["fields"]["Applicant ID"]:
            personal_data = {
                "name": personal_record["fields"]["Full Name"],
                "location": personal_record["fields"]["Location"],
                "email": personal_record["fields"]["Email"],
                "linkedin": personal_record["fields"]["LinkedIn"],
            }
            break

    experience_data = []
    for experience_record in experience_records:
        if experience_record.get("fields", {}).get("Applicant") is not None and applicant_id == experience_record["fields"]["Applicant ID"]:
            experience_data.append({
                "company": experience_record["fields"]["Company"],
                "title": experience_record["fields"]["Title"],
                "start": experience_record["fields"]["Start"],
                "end": experience_record["fields"]["End"],
                "technologies": experience_record["fields"]["Technologies"].split(","),
            })
    
    salary_data = {}
    for salary_record in salary_records:
        if salary_record.get("fields", {}).get("Applicant") is not None and applicant_id == salary_record["fields"]["Applicant ID"]:
            salary_data = {
                "rate": int(salary_record["fields"]["Preferred Rate"]),
                "min_rate": int(salary_record["fields"]["Minimum Rate"]),
                "currency": salary_record["fields"]["Currency"],
                "availability": int(salary_record["fields"]["Availability (hrs/wk)"]),
            }
            break

    compressed_json = {
        "personal": personal_data,
        "experience": experience_data,
        "salary": salary_data,
    }
    return compressed_json


def sanitize_json_records(records):
    """
    Sanitize final applicants records by including only id and fields.
    """
    cleaned_records = []
    for record in records:
        cleaned_record = {
            "id": record["id"],
            "fields": record["fields"]
        }
        cleaned_records.append(cleaned_record)
    return cleaned_records


def upsert_applicants_records(final_applicants_records):
    """
    Upsert applicants records to Applicants table.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLES['applicants']}"
    payload = { "records": final_applicants_records }

    try:
        response = requests.patch(
            url,
            headers=HEADERS,
            json=payload
        )
        if response.status_code == 200:
            print(f"Upserted to Applicants table")
        else:
            raise Exception(f"Failed to upsert to Applicants table: {response.status_code} {response.text}")

    except Exception as ex:
        raise Exception(f"Failed to upsert to Applicants table: {ex}")


def main():
    """
    Main function to fetch all records from all tables.
    """
    applicants_records = fetch_records_from_table(TABLES["applicants"])
    experience_records = fetch_records_from_table(TABLES["experience"])
    personal_records = fetch_records_from_table(TABLES["personal"])
    salary_records = fetch_records_from_table(TABLES["salary"])

    print(f"Fetched {len(applicants_records)} applicants records")
    print(f"Fetched {len(experience_records)} experience records")
    print(f"Fetched {len(personal_records)} personal records")
    print(f"Fetched {len(salary_records)} salary records")

    # Save records to JSON files
    os.makedirs("data", exist_ok=True)

    with open("data/applicants.json", "w") as f:
        json.dump(applicants_records, f, indent=4)
        print(f"Saved {len(applicants_records)} applicants records to data/applicants.json")

    with open("data/experience.json", "w") as f:
        json.dump(experience_records, f, indent=4)
        print(f"Saved {len(experience_records)} experience records to data/experience.json")

    with open("data/personal.json", "w") as f:
        json.dump(personal_records, f, indent=4)
        print(f"Saved {len(personal_records)} personal records to data/personal.json")

    with open("data/salary.json", "w") as f:
        json.dump(salary_records, f, indent=4)
        print(f"Saved {len(salary_records)} salary records to data/salary.json")

    # Build compressed JSON for entire applicants records
    final_applicants_records = []
    for applicant_record in applicants_records:
        applicant_compressed_json = build_compressed_json(applicant_record, experience_records, personal_records, salary_records)
        updated_applicant_record = deepcopy(applicant_record)
        updated_applicant_record["fields"]["Compressed JSON"] = json.dumps(applicant_compressed_json)
        final_applicants_records.append(updated_applicant_record)

    with open("data/final_applicants_records.json", "w") as f:
        json.dump(final_applicants_records, f, indent=4)
        print(f"Saved {len(final_applicants_records)} final applicants records to data/final_applicants_records.json")

    # Sanitize records and upsert 10 records at a time
    sanitized_records = sanitize_json_records(final_applicants_records)
    i = 0
    while i < len(sanitized_records):
        j = min(i + 10, len(sanitized_records))
        print(f"Upserting applicants records in batch from index {i} to {j}")
        upsert_applicants_records(sanitized_records[i:j])
        i = j


if __name__ == "__main__":
    main()

import json
from utils.config_loader import TABLES   
from utils.airtable_operations import fetch_records_from_table, upsert_records


def create_personal_details_record(applicant_id, personal_data, personal_details_record_id, applicant_record_id):
    """
    Create a personal details record.
    """
    updated_personal_details_record = {
        "id": personal_details_record_id,
        "fields": {
            "Applicant": [
                applicant_record_id
            ],
            "Applicant ID": applicant_id,
            "Full Name": personal_data["name"],
            "Location": personal_data["location"],
            "Email": personal_data["email"],
            "LinkedIn": personal_data["linkedin"]
        }
    }
    return updated_personal_details_record


def create_work_experience_records(applicant_id, experience_data, work_experience_record_ids, applicant_record_id):
    """
    Create a work experience record.
    """
    updated_work_experience_records = []
    for i, work_experience_record_id in enumerate(work_experience_record_ids):
        updated_work_experience_record = {
            "id": work_experience_record_id,
            "fields": {
                "Applicant": [
                    applicant_record_id
                ],
                "Applicant ID": applicant_id,
                "Company": experience_data[i]["company"],
                "Title": experience_data[i]["title"],
                "Start": experience_data[i]["start"],
                "End": experience_data[i]["end"],
                "Technologies": ",".join(experience_data[i]["technologies"])
            }
        }
        updated_work_experience_records.append(updated_work_experience_record)
    return updated_work_experience_records


def create_salary_preferences_record(applicant_id, salary_data, salary_preferences_record_id, applicant_record_id):
    """
    Create a salary preferences record.
    """
    updated_salary_preferences_record = {
        "id": salary_preferences_record_id,
        "fields": {
            "Applicant": [
                applicant_record_id
            ],
            "Applicant ID": applicant_id,
            "Preferred Rate": salary_data["rate"],
            "Minimum Rate": salary_data["min_rate"],
            "Currency": salary_data["currency"],
            "Availability (hrs/wk)": str(salary_data["availability"])
        }
    }
    return updated_salary_preferences_record


def main():
    """
    Decompress applicants records.
    """
    applicants_records = fetch_records_from_table(TABLES["applicants"])
    print(f"Found {len(applicants_records)} applicant records.")

    for i, applicant_record in enumerate(applicants_records):
        print(f"Processing applicant {i+1} of {len(applicants_records)}: {applicant_record['fields']['Applicant ID']}")

        applicant_fields = applicant_record.get("fields", {})
        applicant_id = applicant_fields["Applicant ID"]
        compressed_json = applicant_fields["Compressed JSON"]
        personal_details_reference = applicant_fields.get("Personal Details", [])
        work_experience_references = applicant_fields.get("Work Experience", [])
        salary_preferences_reference = applicant_fields.get("Salary Preferences", [])

        # Decompress JSON for the applicant
        if not compressed_json or not applicant_id:
            print(f"Skipping {applicant_id} because it doesn't have applicant ID or compressed JSON")
            continue

        try:
            compressed_json_data = json.loads(compressed_json)

        except Exception as ex:
            print(f"Skipping invalid JSON for {applicant_id}: {ex}")
            continue

        # Insert updated Personal Details record
        if compressed_json_data["personal"] and personal_details_reference:
            personal_details_record = create_personal_details_record(
                applicant_id=applicant_id,
                personal_data=compressed_json_data["personal"],
                personal_details_record_id=personal_details_reference[0],
                applicant_record_id=applicant_record["id"]
            )

            print(f"Upserting personal details record for {applicant_id}")
            upsert_records(
                table_id=TABLES["personal"],
                table_name="Personal Details",
                sanitized_records=[personal_details_record]
            )

        else:
            print(f"Skipping Personal Details for Applicant ID: {applicant_id} because it doesn't have personal details")
        
        # Insert updated Work Experience records
        if compressed_json_data["experience"] and work_experience_references:
            work_experience_records = create_work_experience_records(
                applicant_id=applicant_id,
                experience_data=compressed_json_data["experience"],
                work_experience_record_ids=work_experience_references,
                applicant_record_id=applicant_record["id"]
            )

            i = 0
            while i < len(work_experience_records):
                j = min(i + 10, len(work_experience_records))
                print(f"Upserting {len(work_experience_records[i:j])} work experience records in batch from index {i} to {j}")
                upsert_records(
                    table_id=TABLES["experience"],
                    table_name="Work Experience",
                    sanitized_records=work_experience_records[i:j]
                )
                i = j

        else:
            print(f"Skipping Work Experience for Applicant ID: {applicant_id} because it doesn't have work experience")

        # Insert updated Salary Preferences record
        if compressed_json_data["salary"] and salary_preferences_reference:
            salary_preferences_record = create_salary_preferences_record(
                applicant_id=applicant_id,
                salary_data=compressed_json_data["salary"],
                salary_preferences_record_id=salary_preferences_reference[0],
                applicant_record_id=applicant_record["id"]
            )

            print(f"Upserting salary preferences record for {applicant_id}")
            upsert_records(
                table_id=TABLES["salary"],
                table_name="Salary Preferences",
                sanitized_records=[salary_preferences_record]
            )

        else:
            print(f"Skipping Salary Preferences for Applicant ID: {applicant_id} because it doesn't have salary preferences")

        print(f"Completed processing applicant {i+1} of {len(applicants_records)}: {applicant_record['fields']['Applicant ID']}")


if __name__ == "__main__":
    main()

import json
from openai import OpenAI
import time
from utils.config_loader import TABLES, OPENAI_API_KEY
from utils.airtable_operations import fetch_records_from_table, sanitize_records, upsert_records


client = OpenAI(api_key=OPENAI_API_KEY)


def build_validation_prompt(compressed_json):
    """
    Build a validation prompt for the applicant.
    """
    return f"""
    You are a recruiting analyst. Given this JSON applicant profile, do four things:
    1. Provide a concise 75-word summary.
    2. Rate overall candidate quality from 1-10 (higher is better).
    3. List any data gaps or inconsistencies you notice.
    4. Suggest up to three follow-up questions to clarify gaps.

    Return exactly in the following format:
    Summary: <text>
    Score: <integer>
    Issues: <comma-separated list or 'None'>
    Follow-Ups: <bullet list>

    JSON:
    {compressed_json}
    """


def call_openai_api(prompt, retries=3):
    """
    Call the OpenAI API to get a response for the prompt.
    """
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content

        except Exception as ex:
            print(f"OpenAI API error: {ex}")
            time.sleep(2 ** i)

    return None


def parse_llm_response(response):
    """
    Parse the response from the OpenAI API.
    """
    llm_result = {"LLM Summary": "", "LLM Score": 0, "LLM Follow-Ups": ""}
    try:
        lines = response.splitlines()
        for line in lines:
            if line.startswith("Summary:"):
                llm_result["LLM Summary"] = line[len("Summary:"):].strip()
            elif line.startswith("Score:"):
                llm_result["LLM Score"] = int(line[len("Score:"):].strip())
            elif line.startswith("Follow-Ups:"):
                llm_result["LLM Follow-Ups"] = "\n".join(lines[lines.index(line)+1:]).strip()

    except Exception as ex:
        print(f"Failed to parse response: {ex}")

    return llm_result


def create_updated_applicant_record(applicant_id, llm_result, applicant_record_id):
    """
    Create an updated applicant record.
    """
    updated_applicant_record = {
        "id": applicant_record_id,
        "fields": {
            "Applicant ID": applicant_id,
            "LLM Summary": llm_result["LLM Summary"],
            "LLM Score": llm_result["LLM Score"],
            "LLM Follow-Ups": llm_result["LLM Follow-Ups"],
        }
    }
    return updated_applicant_record


def main():
    """
    Process applicants records to get shortlisted leads and update applicants records
    """
    final_applicants_records = []

    # Fetch applicants records and process them one by one
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

        if shortlist_status in ["Waiting", "Invalid"]:
            print(f"Skipping {applicant_id} because it's already processed. Shortlist Status: {shortlist_status}")
            continue

        try:
            compressed_json_data = json.loads(compressed_json)
        except Exception as ex:
            print(f"Skipping invalid JSON for {applicant_id}: {ex}")
            continue

        prompt = build_validation_prompt(compressed_json)
        response = call_openai_api(prompt)
        if not response:
            print(f"Skipping {applicant_id} because no response from OpenAI API")
            continue

        llm_result = parse_llm_response(response)
        updated_applicant_record = create_updated_applicant_record(
            applicant_id=applicant_id,
            llm_result=llm_result,
            applicant_record_id=applicant_record["id"]
        )
        final_applicants_records.append(updated_applicant_record)

    # # Save final applicants records to a file
    # with open("data/llm_updated_applicants_records.json", "w") as f:
    #     json.dump(final_applicants_records, f, indent=4)
    #     print(f"Saved {len(final_applicants_records)} final applicants records to data/llm_updated_applicants_records.json")

    # Upsert final applicants records
    sanitized_final_applicants_records = sanitize_records(final_applicants_records)
    i = 0
    while i < len(sanitized_final_applicants_records):
        j = min(i + 10, len(sanitized_final_applicants_records))
        print(f"Creating {len(sanitized_final_applicants_records[i:j])} new applicants records in batch from index {i} to {j}")
        upsert_records(
            table_id=TABLES["applicants"],
            table_name="Applicants",
            sanitized_records=sanitized_final_applicants_records[i:j],
            use_post=False
        )
        i = j

    print("Applicants evaluation completed successfully!!!")


if __name__ == "__main__":
    main()

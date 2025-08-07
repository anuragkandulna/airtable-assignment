import requests
from utils.config_loader import HEADERS, AIRTABLE_BASE_ID


def sanitize_records(records):
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
        print(f"Error fetching records from {table_id} table: {ex}")
        return []


def upsert_records(table_id, table_name, sanitized_records, use_post=False):
    """
    Upsert records to a given table using POST or PATCH method.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_id}"
    payload = { "records": sanitized_records }

    try:
        if use_post:
            response = requests.post(
                url,
                headers=HEADERS,
                json=payload
            )
        else:
            response = requests.patch(
                url,
                headers=HEADERS,
                json=payload
            )

        if response.status_code == 200:
            print(f"Upserted {len(sanitized_records)} records to {table_name} table successfully.")
        else:
            print(f"Failed to upsert to {table_name} table due to error {response.status_code}: {response.text}")
            raise Exception(f"Failed to upsert to {table_name} table due to error {response.status_code}: {response.text}")

    except Exception as ex:
        print(f"Failed to upsert to {table_name} table: {ex}")

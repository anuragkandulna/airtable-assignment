import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Airtable basic details
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')

# Airtable Table IDs
APPLICANTS_TABLE_ID = os.getenv('APPLICANTS_TABLE_ID')
PERSONAL_DETAILS_TABLE_ID = os.getenv('PERSONAL_DETAILS_TABLE_ID')
WORK_EXPERIENCE_TABLE_ID = os.getenv('WORK_EXPERIENCE_TABLE_ID')
SALARY_PREFERENCES_TABLE_ID = os.getenv('SALARY_PREFERENCES_TABLE_ID')
SHORTLISTED_LEADS_TABLE_ID = os.getenv('SHORTLISTED_LEADS_TABLE_ID')


# Raise exceptions if variable not found
if not OPENAI_API_KEY:
    raise ValueError('OPENAI_API_KEY not found in .env file.')

if not AIRTABLE_BASE_ID:
    raise ValueError('AIRTABLE_BASE_ID not found in .env file.')

if not AIRTABLE_API_KEY:
    raise ValueError('AIRTABLE_API_KEY not found in .env file.')

if not APPLICANTS_TABLE_ID:
    raise ValueError('APPLICANTS_TABLE_ID not found in .env file.')

if not PERSONAL_DETAILS_TABLE_ID:
    raise ValueError('PERSONAL_DETAILS_TABLE_ID not found in .env file.')

if not WORK_EXPERIENCE_TABLE_ID:
    raise ValueError('WORK_EXPERIENCE_TABLE_ID not found in .env file.')

if not SALARY_PREFERENCES_TABLE_ID:
    raise ValueError('SALARY_PREFERENCES_TABLE_ID not found in .env file.')

if not SHORTLISTED_LEADS_TABLE_ID:
    raise ValueError('SHORTLISTED_LEADS_TABLE_ID not found in .env file.')


# Create constants for Airtable API requests
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

TABLES = {
    "applicants": APPLICANTS_TABLE_ID,
    "personal": PERSONAL_DETAILS_TABLE_ID,
    "experience": WORK_EXPERIENCE_TABLE_ID,
    "salary": SALARY_PREFERENCES_TABLE_ID,
    "shortlisted": SHORTLISTED_LEADS_TABLE_ID
}

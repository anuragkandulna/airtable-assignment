# Airtable Automation

## Overview

This Airtable base manages contractor application data using a multi-table design, automation workflows, and Python scripts for compression, decompression, lead shortlisting and LLM-based evaluation.

-   **Github**: https://github.com/anuragkandulna/airtable-assignment

-   **Airtable Base**: https://airtable.com/appKvwNAhloGjoITk/shrZLsLb602GaLQS5

-   **Personal Details Form**: https://airtable.com/appKvwNAhloGjoITk/pagT4Ko7zkwnzuG6w/form
-   **Work Experience Form**: https://airtable.com/appKvwNAhloGjoITk/pagQbxAimK0F46trc/form
-   **Salary Preferences Form**: https://airtable.com/appKvwNAhloGjoITk/pagrCaERoblFD6R2b/form

-   **Applicant Automation for Personal Data Form**: https://airtable.com/appKvwNAhloGjoITk/wfl5KWdu46vbxOgUW
-   **Applicant Automation for Work Experience Form**: https://airtable.com/appKvwNAhloGjoITk/wflSEvZEz7Y04En80
-   **Applicant Automation for Salary Preferences Form**: https://airtable.com/appKvwNAhloGjoITk/wflvxGdoS9NsgkTIi

---

## Github Project Setup

1. Clone github repository locally using command: `git clone git@github.com:anuragkandulna/airtable-assignment.git` or `git clone https://github.com/anuragkandulna/airtable-assignment.git`
2. Change directory: `cd airtable-assignment`
3. Create a python virtual environment (python must me installed first): `python -m venv venv`
4. Active python virtual environment: `source venv/bin/activate`
5. Install python dependencies fromm requirements file: `pip install -r requirements.txt`
6. Create environment variables file by copying all contents of example file: `cp .env.example .env`
7. Manually edit and add valid secrets of OpenAI and Airtable base. Refer official documentation if needed.
8. Project setup is completed and ready to execute the scripts.

---

## End-to-end workflow

1. Go to form links (given above) and submit records with **Email** as Applicant ID.
2. Once valid submissions are done, run compression script to automate child tables compression and updation in Applicants table: `python compress_json.py`
3. (Optional) In case of JSON edits and automate child table population by run decompression script: `python decompress_json.py`
4. Automate leads generation by running shortlisting script: `python shortlist_leads.py`
5. Automate LLM based evaluation by running evaluation script: `python evaluate_applicants.py`
6. Follow up with potential leads by referring to `Shortlisted Leads` table.
7. Manually select or reject applicant from `Applicants` table.

---

## Tables and Field Definitions

### 1. Applicants

Description: Stores master applicant records and references to related child tables.
Primary Key Field: **Applicant ID**
Condition: By default, Email is considered as Applicant ID to maintain consistency across tables and follow best developer practices.

**Fields:**

-   **Applicant ID** (Email) – Unique email ID of the applicant. (Autofilled by **Applicant Automation for Personal Data Form**)
-   **Shortlist Status** (Single select) – Values: Waiting, Processing, Selected, Rejected, Invalid.
-   **Compressed JSON** (Long text) – JSON representation of the applicant’s profile.
-   **Personal Details** (Linked record) – Link to _Personal Details_ table.
-   **Work Experience** (Linked record) – Link to _Work Experience_ table.
-   **Salary Preferences** (Linked record) – Link to _Salary Preferences_ table.
-   **LLM Summary** (Long text) – Generated summary from LLM.
-   **LLM Score** (Number) – Candidate quality score (1–10) from LLM.
-   **LLM Follow-Ups** (Long text) – Suggested follow-up questions from LLM.
-   **Personal Details** (Linked record) - Link to _Personal Details_ table. (Autofilled by Airtable)
-   **Work Experience** (Linked record) - Link to _Work Experience_ table. (Autofilled by Airtable)
-   **Salary Preferences** (Linked record) - Link to _Salary Preferences_ table. (Autofilled by Airtable)
-   **Shortlisted Leads** (Linked record) - Link to _Shortlisted Leads_ table. (Autofilled by Airtable)

---

### 2. Personal Details

Description: Stores basic information about the applicant upon successful first submission **Personal Data Form**. Duplicate or invalid submissions are still recorded by not linked to **Applicants** table.
Primary Key: **Applicant ID**
Condition: User provided Email must be same as Applicant ID only then record is inserted in **Applicants** table.

**Fields:**

-   **Applicant ID** (Email) - Unique email ID of the applicant. (Given by user same as **Email**)
-   **Email** (Email) - Unique email ID of the applicant.
-   **Name** (Single line text) - Full name of the applicant.
-   **Location** (Single line text) - Current location of the applicant.
-   **LinkedIn** (URL) - LinkedIn profile URL of the Applicant.
-   **Applicant** (Linked record) - Link to _Applicants_ table. (Autofilled by **Applicant Automation for Personal Data Form**)

---

### 3. Work Experience

Description: Stores work history information of the applicant and can be filled after submitting **Personal Details Form**. Invalid submissions are still recorded by not linked to **Applicants** table.
Primary Key: **Applicant ID**
Condition: Applicant ID must be same as user Email and only then record is linked with **Applicants** table.

**Fields:**

-   **Applicant ID** (Email) - Unique email ID of the applicant. (Given by user same as **Email**)
-   **Company** (Single line text) - Company where applicant previously worked.
-   **Title** (Single line text) - Offical designation given by Company to applicant.
-   **Start** (Date) - First working day of applicant for the respective designation.
-   **End** (Date) - Last working day of applicant for the respective designation.
-   **Technologies** (Multiline text) - Comma separated list of technologies applicant is familiar with.
-   **Applicant** (Linked record) - Link to _Applicants_ table. (Autofilled by **Applicant Automation for Work Experience Form**)

---

### 4. Salary Preferences

Description: Stores applicant compensation expectations and can be filled after submitting **Personal Data Form**. Invalid submissions are still recorded by not linked to **Applicants** table.
Primary Key: **Applicant ID**
Condition: Applicant ID must be same as user Email and only then record is linked with **Applicants** table.

**Fields:**

-   **Applicant ID** (Email) - Unique email ID of the applicant. (Given by user same as **Email**)
-   **Preferred Rate** (Number) - Preferred hourly rate given by applicant.
-   **Minimum Rate** (Number) - Minimum hourly rate given by applicant.
-   **Currency** (Single select) - Preferred currency from a predefined list.
-   **Availability (hrs/wk)** (Single select) - Numbers of hours applicant can commit per weekly basis.
-   **Applicant** (Linked record) - Link to _Applicants_ table. (Autofilled by **Applicant Automation for Salary Preferences Form**)

---

### 5. Shortlisted Leads

Description: Holds records of shortlisted candidates based on predefined multi-factor rules. Populated by **Lead Shortlisting Script**.
Primary Key: **Applicant ID**
Condition: Populated after evaluations of compressed json for each record in **Applicants** table.

**Fields:**

-   **Applicant ID** (Email) - Unique email ID of the applicant. (Same as applicant **Email**)
-   **Applicant** (Linked record) - Link to _Applicants_ table.
-   **Compressed JSON** (Long text) - Compressed JSON created by combining child table.
-   **Score Reason** (Long text) - Well defined reason filled by script.
-   **Created At** (Created time) - Timestamp recorded by Airtable at time of record creation.

---

## Airtable Automations

### Personal Details Form Automation

Handles records linking of **Personal Details** table with its parent **Applicants**.

1. **Trigger** – When a record is created in _Personal Details_.
2. **Action** – Finds matching Applicant ID in _Applicants_ table.
    - If found → Updates `Applicant` field in _Personal Details_.
    - If not found → Creates new _Applicants_ record.

---

### Work Experience Form Automation

Handles records linking of **Work Experience** table with its parent **Applicants**.

1. **Trigger** – When a record is created in _Work Experience_.
2. **Action** – Finds matching Applicant ID in _Applicants_ table.
    - If found → Links `Applicant` field in _Work Experience_.
    - If not found → Skips linking.

---

### Salary Preferences Form Automation

Handles records linking of **Salary Preferences** table with its parent **Applicants**.

1. **Trigger** – When a record is created in _Salary Preferences_.
2. **Action** – Finds matching Applicant ID in _Applicants_ table.
    - If found → Links `Applicant` field in _Salary Preferences_.
    - If not found → Skips linking.

---

## Python Scripts

### 1. JSON Compression Script

Filename: `compress_json.py`

-   **Purpose**: Merges data from _Personal Details_, _Work Experience_, and _Salary Preferences_ into a single JSON object per applicant.
-   **Process**:
    1. Fetch applicants and their linked records.
    2. Build JSON structure.
    3. Update `Compressed JSON` in _Applicants_.
-   **Note**: Marks applicants as "Invalid" if incomplete.

---

### 2. JSON Decompression Script

Filename: `decompress_json.py`

-   **Purpose**: Reads `Compressed JSON` from _Applicants_ and pushes it back to child tables.
-   **Rules**:
    -   Uses `Applicant ID` to find matching child records.
    -   Updates only present keys in JSON.

---

### 3. Lead Shortlisting Script

Filename: `shortlist_leads.py`

-   **Rules**:
    -   **Experience**: ≥ 4 years or worked at Tier-1 companies.
    -   **Compensation**: Preferred Rate ≤ $100/hour **and** Availability ≥ 20 hrs/week.
    -   **Location**: Must be in US, Canada, UK, Germany, or India.
-   **Output**:
    -   Creates _Shortlisted Leads_ record.
    -   Links to _Applicants_.
    -   Copies `Compressed JSON` and well defined score reason.

---

### 4. LLM Evaluation Script

Filename: `evaluate_applicants.py`

-   **Trigger**: After `Compressed JSON` is created/updated.
-   **Auth**: Reads OpenAI API key from environment variable.
-   **Prompt**:

    ```
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
    ```

-   **Output Fields**: Updates `LLM Summary`, `LLM Score`, and `LLM Follow-Ups` in _Applicants_.

---

### 4. Utilities - Airtable Operations Script

Filename: `utils/airtable_operations.py`

-   **Auth**: Uses Airtable token from environment variables.
-   **Purpose**: Provides methods to easily operate on Airtable API endpoints.

---

### 5. Utilities - Config Loader Script

Filename: `utils/config_loader.py`

-   **Purpose**: Read environment variables from `.env` for entire project.

---

## Other Files

1. Example environment file - `.env.example`
2. Python requirements file - `requirements.txt`

---

## General Security Notes

-   No API keys are hard-coded.
-   All secrets and environment variables stored loaded from local environment variable text file `.env`
-   Automations skip linking if `Applicant ID` is not found, preventing orphan data.
-   Token usage for LLM calls capped at 1000 tokens to prevent abuse.

---

## Extending Shortlist Criteria

Target filename: `shortlist_leads.py`

-   Update Python shortlisting script with new logic if and when needed.
-   Tier-1 companies list can be updated in `TIER_1_COMPANIES` variable.
-   Allowed locations list can be updated in `ALLOWED_LOCATIONS` variable.
-   Different experience thresholds can be added with new logic.
-   Additional skill-based checks can be introduced with new logic.
-   Update _Shortlisted Leads_ table to capture new fields if required.

---

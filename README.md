# Airtable Automation

## Overview

This Airtable base manages contractor application data using a multi-table design, automation workflows, and Python scripts for compression, decompression, lead shortlisting, and LLM-based evaluation.

---

## Tables and Field Definitions

### 1. Applicants

Stores master applicant records and references to related tables.

**Fields:**

-   **Applicant ID** (Email) – Unique email ID of the applicant.
-   **Shortlist Status** (Single select) – Values: Waiting, Processing, Selected, Rejected, Invalid.
-   **Compressed JSON** (Long text) – JSON representation of the applicant’s profile.
-   **Personal Details** (Linked record) – Link to _Personal Details_ table.
-   **Work Experience** (Linked record) – Link to _Work Experience_ table.
-   **Salary Preferences** (Linked record) – Link to _Salary Preferences_ table.
-   **LLM Summary** (Long text) – Generated summary from LLM.
-   **LLM Score** (Number) – Candidate quality score (1–10) from LLM.
-   **LLM Follow-Ups** (Long text) – Suggested follow-up questions from LLM.

---

### 2. Personal Details

Captures basic information about the applicant.

**Fields:**

-   **Applicant ID** (Email)
-   **Name** (Single line text)
-   **Location** (Single line text)
-   **LinkedIn** (URL)
-   **Applicant** (Linked record to Applicants)

---

### 3. Work Experience

Stores one-to-many work history for each applicant.

**Fields:**

-   **Applicant ID** (Email)
-   **Company** (Single line text)
-   **Title** (Single line text)
-   **Start Date** (Date)
-   **End Date** (Date)
-   **Technologies** (Multiline text)
-   **Applicant** (Linked record to Applicants)

---

### 4. Salary Preferences

Stores applicant compensation expectations.

**Fields:**

-   **Applicant ID** (Email)
-   **Preferred Rate** (Number)
-   **Minimum Rate** (Number)
-   **Currency** (Single select)
-   **Availability** (Single select – hours/week)
-   **Applicant** (Linked record to Applicants)

---

### 5. Shortlisted Leads

Holds records of shortlisted candidates.

**Fields:**

-   **Applicant** (Linked record to Applicants)
-   **Compressed JSON** (Long text)
-   **Score Reason** (Long text)

---

## Automations

### Personal Details Form Automation

1. **Trigger** – When a record is created in _Personal Details_.
2. **Action** – Finds matching Applicant ID in _Applicants_ table.
    - If found → Updates `Applicant` field in _Personal Details_.
    - If not found → Creates new _Applicants_ record.

---

### Work Experience Form Automation

1. **Trigger** – When a record is created in _Work Experience_.
2. **Action** – Finds matching Applicant ID in _Applicants_ table.
    - If found → Links `Applicant` field in _Work Experience_.
    - If not found → Skips linking.

---

### Salary Preferences Form Automation

1. **Trigger** – When a record is created in _Salary Preferences_.
2. **Action** – Finds matching Applicant ID in _Applicants_ table.
    - If found → Links `Applicant` field in _Salary Preferences_.
    - If not found → Skips linking.

---

## Python Scripts

### 1. JSON Compression Script

-   **Purpose**: Merges data from _Personal Details_, _Work Experience_, and _Salary Preferences_ into a single JSON object per applicant.
-   **Process**:
    1. Fetch applicants and their linked records.
    2. Build JSON structure.
    3. Update `Compressed JSON` in _Applicants_.
-   **Note**: Marks applicants as "Invalid" if incomplete.

---

### 2. JSON Decompression Script

-   **Purpose**: Reads `Compressed JSON` from _Applicants_ and pushes it back to child tables.
-   **Rules**:
    -   No data pruning.
    -   Uses `Applicant ID` to find matching child records.
    -   Updates only present keys in JSON.

---

### 3. Lead Shortlisting Script

-   **Rules**:
    -   **Experience**: ≥ 4 years or worked at Tier-1 companies.
    -   **Compensation**: Preferred Rate ≤ $100/hour **and** Availability ≥ 20 hrs/week.
    -   **Location**: Must be in US, Canada, UK, Germany, or India.
-   **Output**:
    -   Creates _Shortlisted Leads_ record.
    -   Links to _Applicants_.
    -   Copies `Compressed JSON` and score reason.

---

### 4. LLM Evaluation Script

-   **Trigger**: After `Compressed JSON` is created/updated.
-   **Auth**: Reads OpenAI API key from Airtable Secret or environment variable.
-   **Prompt**:
-   **Output Fields**: Updates `LLM Summary`, `LLM Score`, and `LLM Follow-Ups` in _Applicants_.

---

## Security Notes

-   No API keys are hard-coded.
-   OpenAI API key stored in Airtable Secret or environment variables.
-   Automations skip linking if `Applicant ID` is not found, preventing orphan data.
-   Token usage for LLM calls capped; repeated calls skipped unless JSON changes.

---

## Extending Shortlist Criteria

-   Update Python shortlisting script with new logic.
-   Add or modify rules:
-   New locations.
-   Different experience thresholds.
-   Additional skill-based checks.
-   Update _Shortlisted Leads_ table to capture new fields if required.

---

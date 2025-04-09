# ReformHQ Take-Home Assessment

## Overview

This project automates the processing of shipment invoices by:
- Extracting structured data from PDF invoices
- Matching and enriching it with internal shipment records
- Handling exceptions (e.g., unmatched records, missing fields)
- Posting structured records to Airtable

The solution includes:
1. A Python script for parsing, matching, and formatting data.
2. A ReformHQ automation setup for triggering processing workflows and sending notifications.

---

## How to Run the Integration

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/reformhq-shipment-integration.git
cd reformhq-shipment-integration

### 2. Set up virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

###3. Enviornment variables
create .env file in root directory
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME=your_table


###4. Run the Script
python main.py

'''

Design Decisions

Python Script
    •    PDF Parsing: Chose pdfplumber due to its flexibility with extracting semi-structured text from invoices.
    •    CSV Matching: The CSV data is read into a dictionary with CT Numbers as keys for fast lookup. This allows accurate and efficient matching.
    •    Data Normalization: Implemented logic to clean and normalize both CT Numbers and text from the invoice to improve matching accuracy.
    •    Exception Handling:
    •    If CT Number from the invoice is not found in the CSV, the script logs these separately for review.
    •    Missing or malformed fields are flagged but don’t stop the pipeline.
    •    Airtable Integration: Used Airtable’s REST API to push enriched records. Each record is created with key fields like CT_Number, invoice number, invoice date, total, MOT, Office, Direction and calculated code .

ReformHQ Workflow
    1.    Trigger: The Reform workflow allows email as a trigger for the workflow.
    2.    A complex extract is then used to extract the initial four fields, being CT_number, invoice number, invoice date, and total
    3.    A Transform node is then used to strip any non alpha numeric characters extracted from the CT Number
    4.   An exception node is then used to send an email if there was no CT Number to extract
    5.    An enrich node is then used to provide access to a table with values associated by ct number
          - this will check ct number to find macthes
    6.    A transform node is then used to if there is a match to update the values with MOT, Office, Direction and calculation code
    7.   An exception node is then used to send an email if this condition is not met. (i.e there is not a match in the table for CT Number)
    8.    The final step is a POST request node used to connect to the airtable and update with the final values. This is done using the URL and a generated bearer token.

Why This Structure?
    -  Initially was a mistake. I misunderstood the task at hand
    - It allows for scalable automation and human-in-the-loop error handling.
    - Easy to replace components (e.g., replace Airtable with a database later).

⸻

Assumptions
    •    All invoice PDFs contain a CT_Number that can be extracted.
    •    CT Numbers are consistent between invoice documents and the Shipment Table.csv indicative of a match.
    •    ReformHQ supports triggering webhooks or HTTP requests to external processors.
    •    Airtable schema has appropriate columns to receive the structured data.

⸻

Improvements

If given more time, I would:
    -    Take more time understanding the ask
    •    Refactor into a Flask or FastAPI service with endpoints for processing files and checking logs.
    •    Add unit tests for the invoice parser and data matcher.
    •    Implement retry logic for API calls to Airtable.
    •    Integrate Slack or email alerts for failed invoice parsing.

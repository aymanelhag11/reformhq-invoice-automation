import pdfplumber
import re
import pandas as pd
from pyairtable import Table
from dotenv import load_dotenv
import os

def extract_invoice_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for line in text.splitlines():
            if "TOTAL:" in line:
                print("[MATCHING LINE]", line)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
                ##print("---- START OF PDF TEXT ----")
                ##print(page_text)
                ##print("---- END OF PDF TEXT ----")

    ## find CT number            
    ct_match = re.search(r'CT[\W_]*\d{6}', text)
    ct_number = re.sub(r'\W+', '', ct_match.group()) if ct_match else None

    # Find Invoice Number (e.g. Invoice #: 100234)
    invoice_match = re.search(r'Invoice\s*#?:?\s*(\S+)', text, re.IGNORECASE)
    invoice_number = invoice_match.group(1) if invoice_match else None

    # Find Date (e.g. Date: 01/03/2024)
    date_match = re.search(r'Date\s*[:\-]?\s*([\d/.-]+)', text, re.IGNORECASE)
    invoice_date = date_match.group(1) if date_match else None

    # Find Total (e.g. Total: $1,234.56)
    # Find Total using broader keywords
    total_match = re.search(r'TOTAL\s*[:\-]?\s*(USD\s*)?([\d,]+\.\d{2})', text, re.IGNORECASE)
    invoice_total = total_match.group(2) if total_match else None
    return {
        'ct_number': ct_number,
        'invoice_number': invoice_number,
        'invoice_date': invoice_date,
        'invoice_total': invoice_total
    }

def load_shipment_data(file_path='shipment_table.csv'):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    print("Columns in CSV:", df.columns.tolist())

    
    # Clean up CT Numbers (remove spaces, dashes, etc.)
    df['CT number'] = df['CT number'].astype(str).str.replace(r'\W+', '', regex=True)
    
    # Build a dictionary for quick lookups
    shipment_dict = df.set_index('CT number').to_dict('index')
    return shipment_dict

def enrich_shipment_data(ct_number, shipment_dict):
    return shipment_dict.get(ct_number)


def calculate_code(mot, office):
    mot_map = {
        'FCL': '13',
        'LCL': '14'
    }
    office_map = {
        'US': '01',
        'EU': '02'
    }

    first_two = mot_map.get(mot, '00')
    last_two = office_map.get(office, '00')
    return first_two + last_two

load_dotenv()

api_key = os.getenv("AIRTABLE_API_KEY")
base_id = os.getenv("AIRTABLE_BASE_ID")
table_name = os.getenv("AIRTABLE_TABLE_NAME")

print("Loaded from .env:")
print("  API Key:", api_key)
print("  Base ID:", base_id)
print("  Table Name:", table_name)

airtable_table = Table(api_key, base_id, table_name)

def post_to_airtable(data):
    fields = {
        "CT Number": data['ct_number'],
        "Invoice Number": data['invoice_number'],
        "Invoice Date": data['invoice_date'],
        "Invoice Total": float(data['invoice_total'].replace(',', '')) if data['invoice_total'] else None,
        "MOT": data.get('MOT'),
        "Office": data.get('Office'),
        "Direction": data.get('Direction'),
        "Calculated Code": data.get('calculated_code')
    }
    airtable_table.create(fields)
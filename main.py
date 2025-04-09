import os
from utils import extract_invoice_data, load_shipment_data, enrich_shipment_data, calculate_code, post_to_airtable

def main():
    invoice_folder = 'invoices'
    shipment_data = load_shipment_data()

    for filename in os.listdir(invoice_folder):
        if filename.endswith('.pdf'):
            file_path = os.path.join(invoice_folder, filename)
            print(f"\nProcessing: {filename}")

            data = extract_invoice_data(file_path)

            if not data['ct_number']:
                print("  [!] CT Number not found.")
                continue

            print("  CT Number:     ", data['ct_number'])
            print("  Invoice #:     ", data['invoice_number'])
            print("  Invoice Date:  ", data['invoice_date'])
            print("  Invoice Total: ", data['invoice_total'])

            enrichment = enrich_shipment_data(data['ct_number'], shipment_data)
            if not enrichment:
                print("  [!] No shipment data found.")
                continue

            data.update(enrichment)
            data['calculated_code'] = calculate_code(
                enrichment.get('MOT'),
                enrichment.get('Office')
            )

            print("  MOT:            ", data.get('MOT'))
            print("  Office:         ", data.get('Office'))
            print("  Direction:      ", data.get('Direction'))
            print("  Calculated Code:", data.get('calculated_code'))

            post_to_airtable(data)
            print("  [✓] Posted to Airtable!")

if __name__ == '__main__':
    main()
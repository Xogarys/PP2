import re     
import json  
import os      


def parse_receipt(text):
    """
    This function takes the raw text of a receipt and turns it into a structured dictionary.
    We'll extract the date, time, store info, products, totals, and VAT.
    """
    receipt = {}  # This dictionary will hold all the information we extract

  
    # Extract date and time

    # Receipts usually show something like: "Время: 06.03.2026 08:45:12"
    date_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})', text)
    if date_match:
        receipt['date'] = date_match.group(1)  # Save the date
        receipt['time'] = date_match.group(2)  # Save the time

   
    # Extract payment info

    # Look for a card payment line like: "Банковская карта: 1234 5678 9012 3456"
    card_match = re.search(r'Банковская карта:\s*([\d\s]+)', text)
    if card_match:
        receipt['payment_method'] = 'Bank Card'  # Note that payment was made by card
        # Clean the number and convert to float
        receipt['payment_amount'] = float(card_match.group(1).replace(' ', ''))

    # Total amount
    total_match = re.search(r'ИТОГО:\s*([\d\s]+)', text)
    if total_match:
        receipt['total'] = float(total_match.group(1).replace(' ', ''))

    # VAT 12%
    vat_match = re.search(r'в т\.ч\. НДС 12%:\s*([\d\s]+)', text)
    if vat_match:
        receipt['vat_12pct'] = float(vat_match.group(1).replace(' ', ''))

  
    # Extract store info
    
    # The BIN number identifies the store officially
    bin_match = re.search(r'БИН\s+(\d+)', text)
    if bin_match:
        receipt['store_bin'] = bin_match.group(1)

    # The store name comes after "Филиал ТОО"
    store_match = re.search(r'Филиал ТОО\s+(.+)', text)
    if store_match:
        receipt['store_name'] = store_match.group(1).strip()

    # The address usually contains "г. <city>, Казахстан, <street>"
    address_match = re.search(r'г\.\s*[\w-]+,Казахстан,\s*(.+)', text)
    if address_match:
        receipt['address'] = address_match.group(0).strip()

    # Extract product details
   
    # Split the receipt text into lines so we can process them one by one
    lines = text.split('\n')
    products = []  # We'll store each product as a dictionary here
    i = 0  # Start at the first line

    # Loop over each line to find product info
    while i < len(lines):
        # Check if the line starts with a number and a dot, like "1."
        num_match = re.match(r'^(\d+)\.$', lines[i].strip())
        if num_match:
            item_num = int(num_match.group(1))  # That's the product number
            name_lines = []  # Some product names can be split across multiple lines
            i += 1  # Move to the next line
            while i < len(lines):
                # Check for the line that contains quantity and unit price like "1,000 x 500,00"
                qty_match = re.match(r'^([\d\s]+),000\s*x\s*([\d\s]+),00$', lines[i].strip())
                if qty_match:
                    qty = float(qty_match.group(1).replace(' ', ''))  # Quantity bought
                    unit_price = float(qty_match.group(2).replace(' ', ''))  # Price per unit
                    i += 1
                    # The next line might have the total price for this item
                    total_line = lines[i].strip() if i < len(lines) else ''
                    total_match2 = re.match(r'^([\d\s]+),00$', total_line)
                    total_price = float(total_match2.group(1).replace(' ', '')) if total_match2 else qty * unit_price
                    i += 1
                    # Sometimes there's a line "Стоимость", we just skip it
                    if i < len(lines) and lines[i].strip() == 'Стоимость':
                        i += 1
                    # Now we save this product into our list
                    products.append({
                        'item': item_num,
                        'name': ' '.join(name_lines).strip(),  # Combine multiple lines of name
                        'quantity': qty,
                        'unit_price': unit_price,
                        'total_price': total_price
                    })
                    break  # Move on to the next product
                else:
                    # If the line is not quantity/price, it must be part of the product name
                    name_lines.append(lines[i].strip())
                    i += 1
        else:
            i += 1  # If line doesn't match a product number, skip it

    # Save all products into the receipt dictionary
    receipt['products'] = products
    receipt['product_count'] = len(products)
    receipt['calculated_total'] = sum(p['total_price'] for p in products)  # Sum of all product totals

    return receipt  # Done parsing the receipt


def main():
    # Get the folder where this script is running
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Specify the input and output files
    input_file = os.path.join(base_dir, 'raw.txt')  # The raw receipt text file
    output_file = os.path.join(base_dir, 'receipt_parsed.json')  # Where we'll save JSON

    # Make sure the input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return

    # Read the content of the receipt
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Parse the receipt
    receipt = parse_receipt(text)

    # Print out the receipt nicely for verification
    print("=" * 60)
    print("PARSED RECEIPT")
    print("=" * 60)
    print(f"Store:          {receipt.get('store_name', 'N/A')}")
    print(f"Date:           {receipt.get('date', 'N/A')} {receipt.get('time', 'N/A')}")
    print(f"Address:        {receipt.get('address', 'N/A')}")
    print(f"Payment Method: {receipt.get('payment_method', 'N/A')}")
    print()
    print(f"{'#':<4} {'Product':<50} {'Qty':>5} {'Price':>10} {'Total':>10}")
    print("-" * 82)
    for p in receipt['products']:
        print(f"{p['item']:<4} {p['name'][:50]:<50} {p['quantity']:>5.0f} {p['unit_price']:>10.2f} {p['total_price']:>10.2f}")
    print("-" * 82)
    print(f"{'TOTAL:':<62} {receipt.get('total', 0):>10.2f}")
    print(f"{'Calculated Total:':<62} {receipt.get('calculated_total', 0):>10.2f}")
    print(f"{'VAT 12%:':<62} {receipt.get('vat_12pct', 0):>10.2f}")
    print()

    # Save everything to JSON for further use
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)

    print(f"JSON saved to {output_file}")


if __name__ == '__main__':
    main()
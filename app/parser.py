import fitz
import re


def extract_number(label, text):
    pattern = rf"{label}\s*-?Rp([\d.]+)"
    match = re.search(pattern, text)
    if match:
        return int(match.group(1).replace(".", ""))
    else:
        return 0


def extract_items_from_pdf(file_path: str):
    doc = fitz.open(file_path)
    text = "\n".join(page.get_text() for page in doc)
    lines = text.splitlines()

    items = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Case 1: Quantity and name in one line (e.g., "2 Nasi Rendang Sapi")
        match_combined = re.match(r"^(\d+)\s+(.+)", line)
        if match_combined:
            qty = int(match_combined.group(1))
            name = match_combined.group(2).strip()

            # Check if name might be multiline
            j = i + 1
            while j < len(lines) and not re.match(r"^@Rp[\d.]+$", lines[j].strip()):
                # Skip if next line looks like a quantity (standalone number)
                if re.match(r"^\d+$", lines[j].strip()):
                    break
                name += " " + lines[j].strip()
                j += 1

            # Get unit price and total price
            if j + 1 < len(lines):
                unit_price_line = lines[j].strip()
                total_price_line = lines[j + 1].strip()
                unit_price_match = re.match(r"^@Rp([\d.]+)$", unit_price_line)
                total_price_match = re.match(r"^Rp([\d.]+)$", total_price_line)

                if unit_price_match and total_price_match:
                    unit_price = int(unit_price_match.group(1).replace(".", ""))
                    items.append({
                        "name": name,
                        "quantity": qty,
                        "unit_price": unit_price
                    })
                    i = j + 2
                    continue
        
        # Case 2: Quantity alone in one line (e.g., line has only "2")
        match_qty_only = re.match(r"^(\d+)$", line)
        if match_qty_only and i + 1 < len(lines):
            qty = int(match_qty_only.group(1))
            
            # Look for the name in the next line(s)
            j = i + 1
            name = lines[j].strip()
            
            # Skip empty lines
            while j < len(lines) and not name:
                j += 1
                if j < len(lines):
                    name = lines[j].strip()
            
            if not name:
                i += 1
                continue
                
            # Check if name might be multiline
            k = j + 1
            while k < len(lines) and not re.match(r"^@Rp[\d.]+$", lines[k].strip()):
                # Stop if we encounter another standalone number (next item quantity)
                if re.match(r"^\d+$", lines[k].strip()):
                    break
                name += " " + lines[k].strip()
                k += 1

            # Get unit price and total price
            if k + 1 < len(lines):
                unit_price_line = lines[k].strip()
                total_price_line = lines[k + 1].strip()
                unit_price_match = re.match(r"^@Rp([\d.]+)$", unit_price_line)
                total_price_match = re.match(r"^Rp([\d.]+)$", total_price_line)

                if unit_price_match and total_price_match:
                    unit_price = int(unit_price_match.group(1).replace(".", ""))
                    items.append({
                        "name": name,
                        "quantity": qty,
                        "unit_price": unit_price
                    })
                    i = k + 2
                    continue
        
        i += 1

    total_price = extract_number("Total harga", text)
    handling_fee = extract_number("Biaya penanganan dan pengiriman", text)
    other_fee = extract_number("Biaya lainnya", text)
    discount = extract_number("Diskon(?! PLUS)", text)
    discount_plus = extract_number("Diskon PLUS", text)
    total_payment = extract_number("Total pembayaran", text)
    print(total_price, handling_fee, other_fee, discount, discount_plus, total_payment)

    return items, total_price, handling_fee, other_fee, discount, discount_plus, total_payment
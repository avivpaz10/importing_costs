import pandas as pd
import numpy as np

def find_header_and_columns(df):
    # Define possible header keywords for each field
    header_keywords = {
        'item': ['item', 'code', 'product', 'customer id'],
        'description': ['description', 'desc'],
        'price': ['unit price', 'unite price', 'price', 'cost'],
        'quantity': ['qty', 'quantity', 'sets/ctn', 'pcs', 'amount'],
        'cbm': ['cbm', 'volume', 'm3']
    }
    header_row_idx = None
    column_map = {}

    # Scan first 10 rows for header
    for idx in range(min(10, len(df))):
        row = df.iloc[idx]
        for col_idx, val in enumerate(row):
            if pd.isna(val):
                continue
            val_str = str(val).strip().lower()
            for key, keywords in header_keywords.items():
                if any(k in val_str for k in keywords):
                    column_map[key] = col_idx
        # If we found at least 3 fields, treat this as header
        if len(column_map) >= 3:
            header_row_idx = idx
            break

    return header_row_idx, column_map

def extract_products_from_excel(filepath):
    df = pd.read_excel(filepath, header=None)
    header_row_idx, column_map = find_header_and_columns(df)
    if header_row_idx is None:
        raise ValueError("Could not find a suitable header row.")

    products = []
    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]
        # Stop if the item column is empty or says 'total'
        item_val = row[column_map['item']] if 'item' in column_map else None
        if pd.isna(item_val) or (isinstance(item_val, str) and 'total' in item_val.lower()):
            break
        product = {
            'item': str(item_val).strip() if item_val is not None else '',
            'description': str(row[column_map['description']]).strip() if 'description' in column_map else '',
            'price': float(row[column_map['price']]) if 'price' in column_map and pd.notna(row[column_map['price']]) else 0,
            'quantity': float(row[column_map['quantity']]) if 'quantity' in column_map and pd.notna(row[column_map['quantity']]) else 0,
            'cbm': float(row[column_map['cbm']]) if 'cbm' in column_map and pd.notna(row[column_map['cbm']]) else None
        }
        products.append(product)
    return products

if __name__ == "__main__":
    products = extract_products_from_excel("20240129 invoice.xls")
    for p in products:
        print(p) 
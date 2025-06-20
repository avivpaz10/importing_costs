from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
from datetime import datetime
import os
import re
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_numeric_value(text):
    """Extract numeric value from text, handling various formats."""
    if pd.isna(text):
        return 0
    if isinstance(text, (int, float)):
        return float(text)
    # Remove any non-numeric characters except decimal point
    numeric_str = re.sub(r'[^\d.]', '', str(text))
    try:
        return float(numeric_str)
    except ValueError:
        return 0

def extract_product_info(text):
    """Extract product information from the text field."""
    if pd.isna(text):
        print("Empty text field")
        return None
        
    # Split the text into lines and clean them
    lines = [line.strip() for line in str(text).split('\n') if line.strip()]
    print(f"Raw text: {text}")
    print(f"Extracted lines: {lines}")
    
    if not lines:
        return None
        
    # Extract product code and item number
    first_line = lines[0].strip()
    product_code = first_line.split()[0] if first_line else ''
    print(f"Extracted product code: {product_code}")
    
    item_number = ''
    material = ''
    specs = []
    packing = ''
    
    # Process each line to extract information
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Extract item number
        if 'Item No.' in line:
            try:
                # Handle both '：' and ':' as separators
                item_number = line.split('：')[-1].strip() if '：' in line else line.split(':')[-1].strip()
                print(f"Found item number: {item_number}")
            except:
                print(f"Could not parse item number from: {line}")
            continue
            
        # Extract material
        if 'Material:' in line:
            try:
                material = line.split('Material:')[-1].strip()
                print(f"Found material: {material}")
            except:
                print(f"Could not parse material from: {line}")
            continue
            
        # Extract packing information
        if 'Packing:' in line:
            try:
                packing = line.split('Packing:')[-1].strip()
                print(f"Found packing info: {packing}")
            except:
                print(f"Could not parse packing from: {line}")
            continue
            
        # Add other specifications
        if any(term in line.lower() for term in ['wheel', 'handle', 'deck', 'size', 'color', 'product size', 'y bar']):
            specs.append(line)
            print(f"Added specification: {line}")
    
    # Create a detailed description
    description_parts = []
    if material:
        description_parts.append(f"Material: {material}")
    if specs:
        description_parts.extend(specs)
    if packing:
        description_parts.append(f"Packing: {packing}")
    
    # If we have no description but have other lines, use them
    if not description_parts and len(lines) > 1:
        description_parts.extend(lines[1:])
    
    result = {
        'product_code': product_code,
        'item_number': item_number,
        'description': '\n'.join(description_parts)
    }
    print(f"Final product info: {result}")
    return result

def extract_volume(text):
    """Extract volume information from text."""
    if pd.isna(text):
        return 0
    text = str(text).lower()
    # Look for volume in cbm
    if 'cbm' in text:
        try:
            # Extract the number before 'cbm'
            volume_str = text.split('cbm')[0].strip()
            return float(volume_str)
        except:
            return 0
    return 0

def safe_float_convert(value):
    """Safely convert a value to float, handling empty strings and spaces."""
    if pd.isna(value):
        return 0
    try:
        # Convert to string, strip whitespace, and handle empty strings
        value_str = str(value).strip()
        if not value_str or value_str.isspace() or value_str.lower() == 'nan':
            return 0
        # Remove any currency symbols or commas
        value_str = value_str.replace('$', '').replace(',', '')
        return float(value_str)
    except (ValueError, TypeError):
        return 0

def find_numeric_value(row, search_terms, min_value=0, exclude_cols=None):
    """Search for a numeric value in a row using various search terms."""
    if exclude_cols is None:
        exclude_cols = set()
        
    best_value = 0
    best_col = None
    
    for col_num, value in enumerate(row):
        if col_num in exclude_cols or pd.isna(value):
            continue
            
        value_str = str(value).strip().lower()
        
        # First check if this cell contains any of our search terms
        has_term = any(term in value_str for term in search_terms)
        
        # If this cell has a term, look for numbers in adjacent cells
        if has_term:
            for offset in [-1, 1]:
                check_col = col_num + offset
                if 0 <= check_col < len(row) and check_col not in exclude_cols and pd.notna(row[check_col]):
                    try:
                        num_value = safe_float_convert(row[check_col])
                        if num_value > min_value and num_value > best_value:
                            best_value = num_value
                            best_col = check_col
                    except:
                        continue
        
        # Also check if this cell itself is a number
        try:
            num_value = safe_float_convert(value)
            if num_value > min_value and num_value > best_value:
                # Check adjacent cells for our terms
                for offset in [-1, 1]:
                    check_col = col_num + offset
                    if 0 <= check_col < len(row) and pd.notna(row[check_col]):
                        if any(term in str(row[check_col]).lower() for term in search_terms):
                            best_value = num_value
                            best_col = col_num
                            break
        except:
            continue
    
    return best_value, best_col

def find_column_indices(df):
    """
    Find the column indices for item number, quantity, price, and volume.
    Uses multiple strategies to handle different Excel formats.
    """
    print("\nSearching for header row...")
    
    # Strategy 1: Look for traditional header patterns
    header_row_idx = None
    header_patterns = [
        'Item NO.',
        'Item No.',
        'Item Number',
        'Item',
        'No.',
        'Product',
        'Description'
    ]
    
    for idx, row in df.iterrows():
        if pd.isna(row[0]):
            continue
            
        first_col = str(row[0]).strip()
        # Only consider this a header if it's a short, clean header (not company info)
        if (any(pattern.lower() in first_col.lower() for pattern in header_patterns) and 
            len(first_col) < 50 and  # Avoid long company descriptions
            not any(word in first_col.lower() for word in ['company', 'ltd', 'co', 'tel', 'email', 'website', 'contact'])):
            header_row_idx = idx
            print(f"Found header row at index {idx} (Strategy 1)")
            print("Header row contents:")
            for col_idx, value in enumerate(row):
                if pd.notna(value):
                    print(f"Column {col_idx}: {value}")
            break
    
    # Strategy 2: Look for any row with multiple header-like keywords
    if header_row_idx is None:
        print("Strategy 1 failed, trying Strategy 2...")
        for idx, row in df.iterrows():
            if pd.isna(row[0]):
                continue
                
            # Check if this row has multiple non-empty cells that look like headers
            header_like_cells = 0
            header_content = []
            
            for col_idx, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip().upper()
                    # Look for common header keywords
                    header_keywords = [
                        'ITEM', 'NO', 'NUMBER', 'PRODUCT', 'DESCRIPTION', 'NAME',
                        'QTY', 'QUANTITY', 'PCS', 'PIECES', 'UNITS',
                        'PRICE', 'COST', 'AMOUNT', 'USD', '$', 'UNIT PRICE',
                        'CBM', 'VOLUME', 'SIZE', 'DIMENSION', 'M3', 'CUBIC',
                        'TOTAL', 'SUM', 'GRAND'
                    ]
                    
                    for keyword in header_keywords:
                        if keyword in value_str:
                            header_like_cells += 1
                            header_content.append(f"Col{col_idx}: {value_str}")
                            break
            
            if header_like_cells >= 2:  # At least 2 columns look like headers
                header_row_idx = idx
                print(f"Found header row at index {idx} (Strategy 2)")
                print(f"Header content: {header_content}")
                break
    
    # Strategy 3: Look for the row before the first product-like row
    if header_row_idx is None:
        print("Strategy 2 failed, trying Strategy 3...")
        for idx in range(1, len(df)):
            row = df.iloc[idx]
            if pd.notna(row[0]):
                first_col = str(row[0]).strip()
                # Check if this looks like a product row (alphanumeric content)
                if any(c.isalnum() for c in first_col) and len(first_col) > 2:
                    # Check if previous row might be a header
                    prev_row = df.iloc[idx - 1]
                    if not pd.isna(prev_row[0]):
                        prev_first_col = str(prev_row[0]).strip()
                        # If previous row has short text, it might be a header
                        if len(prev_first_col) < 20 and any(c.isalpha() for c in prev_first_col):
                            header_row_idx = idx - 1
                            print(f"Found header row at index {header_row_idx} (Strategy 3)")
                            print(f"Header: {prev_first_col}")
                            break
    
    if header_row_idx is None:
        print("Could not find header row with any strategy")
        return None
    
    # Get the header row
    header_row = df.iloc[header_row_idx]
    
    # Initialize column indices
    column_indices = {
        'item_no': 0,  # We know this is the first column
        'quantity': None,
        'price': None,
        'volume': None
    }
    
    # Search for each column with more flexible patterns
    price_candidates = []
    unit_price_candidates = []
    total_price_candidates = []
    for col_idx, value in enumerate(header_row):
        if pd.isna(value):
            continue
        value = str(value).strip().upper()

        # Look for quantity column with multiple patterns
        if any(pattern in value for pattern in ['QTY', 'QUANTITY', '(PCS)', 'PCS', 'UNITS', 'PIECES', 'NO.']):
            column_indices['quantity'] = col_idx
            print(f"Found quantity column at {col_idx}: {value}")

        # Look for price column with multiple patterns
        elif any(pattern in value for pattern in ['PRICE', 'COST', 'AMOUNT', 'USD', '$', 'UNIT PRICE', 'RATE']):
            price_candidates.append((col_idx, value))
            print(f"Found price candidate at {col_idx}: {value}")
            # Prioritize unit price columns
            if 'UNIT' in value or 'PER' in value:
                unit_price_candidates.append((col_idx, value))
                print(f"  -> Unit price candidate")
            # If header contains 'TOTAL' or 'AMOUNT', treat as total price
            elif 'TOTAL' in value or 'AMOUNT' in value:
                total_price_candidates.append((col_idx, value))
                print(f"  -> Total price candidate")
            else:
                print(f"  -> Regular price candidate")

        # Look for volume column with multiple patterns
        elif any(pattern in value for pattern in ['CBM', 'VOLUME', 'SIZE', 'DIMENSION', 'M3', 'CUBIC', 'SPACE']):
            column_indices['volume'] = col_idx
            print(f"Found volume column at {col_idx}: {value}")

    print(f"\nPrice candidates found: {len(price_candidates)}")
    for col_idx, value in price_candidates:
        print(f"  Column {col_idx}: {value}")

    # Decide which price column to use
    if unit_price_candidates:
        column_indices['price'] = unit_price_candidates[0][0]
        print(f"Selected unit price column at {unit_price_candidates[0][0]}: {unit_price_candidates[0][1]}")
        if total_price_candidates:
            print(f"Warning: Both unit price and total price columns found. Using unit price column {unit_price_candidates[0][0]}.")
    elif price_candidates:
        if len(price_candidates) == 1:
            # Only one price-like column, use it (old format support)
            column_indices['price'] = price_candidates[0][0]
            print(f"Selected price column at {price_candidates[0][0]}: {price_candidates[0][1]} (single candidate, fallback)")
        else:
            # Prefer one without 'TOTAL' or 'AMOUNT'
            non_total_candidates = [(col_idx, value) for col_idx, value in price_candidates if 'TOTAL' not in value and 'AMOUNT' not in value]
            if non_total_candidates:
                column_indices['price'] = non_total_candidates[0][0]
                print(f"Selected price column at {non_total_candidates[0][0]}: {non_total_candidates[0][1]} (no 'total'/'amount')")
            else:
                # Fallback: pick the leftmost price-like column
                column_indices['price'] = price_candidates[0][0]
                print(f"Warning: Ambiguous price columns, using leftmost at {price_candidates[0][0]}: {price_candidates[0][1]}")
    else:
        print("No price candidates found!")

    # If we didn't find some columns, try to infer them from the data
    if column_indices['quantity'] is None:
        print("Quantity column not found, trying to infer from data...")
        # Look for numeric columns that might be quantity
        for col_idx, value in enumerate(header_row):
            if pd.isna(value):
                continue
            # Check if this column has mostly integer values
            numeric_count = 0
            total_count = 0
            for row_idx in range(header_row_idx + 1, min(header_row_idx + 10, len(df))):
                if pd.notna(df.iloc[row_idx, col_idx]):
                    total_count += 1
                    try:
                        val = float(df.iloc[row_idx, col_idx])
                        if val == int(val) and val > 0:  # Integer and positive
                            numeric_count += 1
                    except:
                        pass
            
            if total_count > 0 and numeric_count / total_count > 0.7:  # 70% are integers
                column_indices['quantity'] = col_idx
                print(f"Inferred quantity column at {col_idx} based on data pattern")
                break
    
    if column_indices['price'] is None:
        print("Price column not found, trying to infer from data...")
        # Look for numeric columns that might be price
        for col_idx, value in enumerate(header_row):
            if pd.isna(value):
                continue
            # Check if this column has decimal values
            decimal_count = 0
            total_count = 0
            for row_idx in range(header_row_idx + 1, min(header_row_idx + 10, len(df))):
                if pd.notna(df.iloc[row_idx, col_idx]):
                    total_count += 1
                    try:
                        val = float(df.iloc[row_idx, col_idx])
                        if val > 0:  # Positive values
                            decimal_count += 1
                    except:
                        pass
            
            if total_count > 0 and decimal_count / total_count > 0.5:  # 50% are positive numbers
                column_indices['price'] = col_idx
                print(f"Inferred price column at {col_idx} based on data pattern")
                break
    
    if column_indices['volume'] is None:
        print("Volume column not found, trying to infer from data...")
        # Look for numeric columns that might be volume (usually smaller decimal values)
        for col_idx, value in enumerate(header_row):
            if pd.isna(value):
                continue
            # Check if this column has small decimal values (typical for volume)
            small_decimal_count = 0
            total_count = 0
            for row_idx in range(header_row_idx + 1, min(header_row_idx + 10, len(df))):
                if pd.notna(df.iloc[row_idx, col_idx]):
                    total_count += 1
                    try:
                        val = float(df.iloc[row_idx, col_idx])
                        if 0 < val < 10:  # Small positive values typical for volume
                            small_decimal_count += 1
                    except:
                        pass
            
            if total_count > 0 and small_decimal_count / total_count > 0.3:  # 30% are small decimals
                column_indices['volume'] = col_idx
                print(f"Inferred volume column at {col_idx} based on data pattern")
                break
    
    # Verify we found at least some required columns
    found_columns = [col for col, idx in column_indices.items() if idx is not None]
    if len(found_columns) < 2:  # Need at least item_no and one other column
        print(f"Warning: Could not find enough columns. Found: {found_columns}")
        print(f"Column indices: {column_indices}")
        return None
    
    print("\nFound column indices:")
    print(f"Item NO.: column {column_indices['item_no']}")
    print(f"Quantity: column {column_indices['quantity']}")
    print(f"Price: column {column_indices['price']}")
    print(f"Volume: column {column_indices['volume']}")
    
    return column_indices

def find_product_rows(df):
    """
    Find the start and end rows for products based on the header row and product code presence.
    Returns a tuple of (start_row, end_row).
    """
    print("\nSearching for product rows...")
    
    # Find the header row with multiple possible patterns
    header_row_idx = None
    header_patterns = [
        'Item NO.',
        'Item No.',
        'Item Number',
        'Item',
        'No.',
        'Product',
        'Description'
    ]
    
    for idx, row in df.iterrows():
        if pd.isna(row[0]):
            continue
            
        first_col = str(row[0]).strip()
        if any(pattern.lower() in first_col.lower() for pattern in header_patterns):
            header_row_idx = idx
            print(f"Found header row at index {idx}")
            break
    
    if header_row_idx is None:
        # Try alternative approach - look for any row with header-like content
        for idx, row in df.iterrows():
            if pd.isna(row[0]):
                continue
                
            # Check if this row has multiple non-empty cells that look like headers
            header_like_cells = 0
            for col_idx, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip().upper()
                    # Look for common header keywords
                    if any(keyword in value_str for keyword in ['QTY', 'QUANTITY', 'PRICE', 'CBM', 'VOLUME', 'AMOUNT', 'COST']):
                        header_like_cells += 1
            
            if header_like_cells >= 2:  # At least 2 columns look like headers
                header_row_idx = idx
                print(f"Found alternative header row at index {idx}")
                break
    
    if header_row_idx is None:
        print("Could not find header row")
        return None, None
    
    # Start row is the next row after the header
    start_row = header_row_idx + 1
    print(f"Product data starts at row {start_row}")
    
    # Find the end row by looking for the first row without a product code
    end_row = None
    
    # Strategy 1: Look for rows without alphanumeric content in first column
    for idx, row in df.iloc[start_row:].iterrows():
        # Skip empty rows
        if row.isna().all():
            continue
            
        # Check if the first column contains a product code
        first_col = str(row[0]).strip() if pd.notna(row[0]) else ''
        if not first_col or not any(c.isalnum() for c in first_col):  # No alphanumeric characters means no product code
            end_row = idx - 1
            print(f"Found end of products at row {end_row} (Strategy 1)")
            break
    
    # Strategy 2: Look for summary/total rows
    if end_row is None:
        for idx, row in df.iloc[start_row:].iterrows():
            if pd.isna(row[0]):
                continue
                
            first_col = str(row[0]).strip().upper()
            # Look for summary keywords
            summary_keywords = ['TOTAL', 'SUM', 'GRAND TOTAL', 'SUBTOTAL', 'TOTALS']
            if any(keyword in first_col for keyword in summary_keywords):
                end_row = idx - 1
                print(f"Found end of products at row {end_row} (Strategy 2 - found summary row)")
                break
    
    # Strategy 3: Look for rows with very different data patterns
    if end_row is None:
        for idx, row in df.iloc[start_row:].iterrows():
            if pd.isna(row[0]):
                continue
                
            # Check if this row has a very different pattern (e.g., all text, no numbers)
            numeric_count = 0
            total_cells = 0
            for col_idx, val in enumerate(row):
                if pd.notna(val):
                    total_cells += 1
                    try:
                        float(val)
                        numeric_count += 1
                    except:
                        pass
            
            # If this row has no numeric data and previous rows did, it might be the end
            if total_cells > 0 and numeric_count == 0:
                # Check if previous rows had numeric data
                prev_row = df.iloc[idx - 1]
                prev_numeric_count = 0
                prev_total_cells = 0
                for col_idx, val in enumerate(prev_row):
                    if pd.notna(val):
                        prev_total_cells += 1
                        try:
                            float(val)
                            prev_numeric_count += 1
                        except:
                            pass
                
                if prev_total_cells > 0 and prev_numeric_count > 0:
                    end_row = idx - 1
                    print(f"Found end of products at row {end_row} (Strategy 3 - data pattern change)")
                    break
    
    # If we didn't find an end row, use the last non-empty row
    if end_row is None:
        for idx in range(len(df) - 1, start_row - 1, -1):
            if not df.iloc[idx].isna().all():
                end_row = idx
                print(f"Using last non-empty row as end: {end_row}")
                break
    
    if end_row is None:
        print("Could not find end of product data")
        return None, None
    
    print(f"Product data range: rows {start_row} to {end_row}")
    return start_row, end_row

def process_excel_data(df):
    """Process Excel data and extract relevant information."""
    print("Starting Excel processing...")
    print(f"DataFrame shape: {df.shape}")
    
    # Find the column indices from the header row
    column_indices = find_column_indices(df)
    if column_indices is None:
        return {'products': [], 'columns_found': {}}
    
    # Find the start and end rows for products
    start_row, end_row = find_product_rows(df)
    if start_row is None or end_row is None:
        return {'products': [], 'columns_found': {}}
    
    print(f"\nProcessing products from row {start_row} to {end_row}")
    
    # Process all products
    products = []
    
    for current_row in range(start_row, end_row + 1):
        row = df.iloc[current_row]
        
        print(f"\nProcessing row {current_row}:")
        
        # Skip completely empty rows
        if row.isna().all():
            print("Skipping empty row")
            continue
            
        # Get the full product information from the first column
        product_text = str(row[0]) if pd.notna(row[0]) else ''
        
        # Skip rows without a product code
        if not any(c.isalnum() for c in product_text):
            print("Skipping row: No product code found")
            continue
        
        # Extract product information
        product_info = extract_product_info(product_text)
        
        if not product_info or not product_info['product_code']:
            print("Skipping row: No valid product code found")
            continue
            
        try:
            # Check if all required columns were found
            if column_indices['quantity'] is None:
                print(f"Error: Quantity column not found")
                continue
            if column_indices['price'] is None:
                print(f"Error: Price column not found")
                continue
            if column_indices['volume'] is None:
                print(f"Error: Volume column not found")
                continue
            
            # Get values from the identified columns
            quantity = safe_float_convert(row[column_indices['quantity']])
            price_per_unit = safe_float_convert(row[column_indices['price']])
            volume = safe_float_convert(row[column_indices['volume']])
            
            print(f"\nFound values for {product_info['product_code']}:")
            print(f"Quantity: {quantity} (col {column_indices['quantity']})")
            print(f"Price per unit: ${price_per_unit:.2f} (col {column_indices['price']})")
            print(f"Volume: {volume} (col {column_indices['volume']})")
            
            # Calculate total price
            total_price = quantity * price_per_unit if quantity > 0 and price_per_unit > 0 else 0
            
            # Only add product if we have at least a product code and either quantity or price
            if product_info['product_code'] and (quantity > 0 or price_per_unit > 0):
                product = {
                    'name': f"{product_info['product_code']} - {product_info['item_number']}",
                    'description': product_info['description'],
                    'quantity': quantity,
                    'total_volume': volume,
                    'cost_per_unit_usd': price_per_unit,
                    'total_price_usd': total_price
                }
                products.append(product)
                print(f"Added product: {product['name']} (Qty: {quantity}, Price per unit: ${price_per_unit:.2f}, Volume: {volume})")
            else:
                print(f"Skipping product: No valid quantity or price found")
        except Exception as e:
            print(f"Error processing row {current_row}, skipping: {e}")
            print(f"Row data: {[str(val) if pd.notna(val) else 'NaN' for val in row]}")
            continue
    
    print(f"\nTotal products found: {len(products)}")
    if products:
        print("\nProducts found:")
        for p in products:
            print(f"- {p['name']}:")
            print(f"  Quantity: {p['quantity']} units")
            print(f"  Price per unit: ${p['cost_per_unit_usd']:.2f}")
            print(f"  Total price: ${p['total_price_usd']:.2f}")
            print(f"  Volume: {p['total_volume']} cbm")
            print(f"  Description: {p['description']}")
    else:
        print("\nNo products were found. Please check the data format.")
    
    return {
        'products': products,
        'columns_found': {
            'name': 'Product Code & Item No.',
            'quantity': f'Column {column_indices["quantity"]} (QTY(PCS))',
            'total_volume': f'Column {column_indices["volume"]} (CBM)',
            'price_per_unit': f'Column {column_indices["price"]} (PRICE)'
        }
    }

def analyze_excel_structure(filepath):
    """
    Analyze the structure of an Excel file to help understand its format.
    """
    try:
        print(f"\nAnalyzing Excel file structure: {filepath}")
        
        # Read the Excel file with fallback for format detection
        df = None
        try:
            if filepath.endswith('.xls'):
                # Try xlrd first for .xls files
                df = pd.read_excel(filepath, header=None, engine='xlrd')
            else:
                # Use openpyxl for .xlsx files
                df = pd.read_excel(filepath, header=None, engine='openpyxl')
        except Exception as e:
            # If xlrd fails, try openpyxl (file might be .xlsx with .xls extension)
            if filepath.endswith('.xls'):
                print(f"xlrd failed, trying openpyxl: {str(e)}")
                try:
                    df = pd.read_excel(filepath, header=None, engine='openpyxl')
                except Exception as e2:
                    print(f"openpyxl also failed: {str(e2)}")
                    raise e2
            else:
                raise e
        
        if df is None:
            raise Exception("Could not read Excel file with any engine")
        
        print(f"File shape: {df.shape} (rows, columns)")
        
        # Show first 15 rows to understand structure
        print("\nFirst 15 rows of the file:")
        for idx in range(min(15, len(df))):
            row = df.iloc[idx]
            row_data = []
            for col_idx, val in enumerate(row):
                if pd.notna(val):
                    val_str = str(val).strip()
                    if len(val_str) > 30:
                        val_str = val_str[:27] + "..."
                    row_data.append(f"Col{col_idx}: {val_str}")
                else:
                    row_data.append(f"Col{col_idx}: <empty>")
            print(f"Row {idx}: {row_data}")
        
        # Look for potential header rows with more flexible patterns
        print("\nSearching for potential header rows...")
        header_candidates = []
        
        for idx in range(min(15, len(df))):
            row = df.iloc[idx]
            if pd.isna(row[0]):
                continue
                
            # Check all columns in this row for header-like content
            header_score = 0
            header_content = []
            
            for col_idx, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip().upper()
                    # Look for common header keywords
                    header_keywords = [
                        'ITEM', 'NO', 'NUMBER', 'PRODUCT', 'DESCRIPTION', 'NAME',
                        'QTY', 'QUANTITY', 'PCS', 'PIECES', 'UNITS',
                        'PRICE', 'COST', 'AMOUNT', 'USD', '$', 'UNIT PRICE',
                        'CBM', 'VOLUME', 'SIZE', 'DIMENSION', 'M3', 'CUBIC',
                        'TOTAL', 'SUM', 'GRAND'
                    ]
                    
                    for keyword in header_keywords:
                        if keyword in value_str:
                            header_score += 1
                            header_content.append(f"Col{col_idx}: {value_str}")
                            break
            
            if header_score >= 2:  # At least 2 columns look like headers
                header_candidates.append((idx, header_score, header_content))
                print(f"Row {idx} - Score {header_score}: {header_content}")
        
        # Look for numeric data patterns in each column
        print("\nAnalyzing numeric data patterns...")
        for col_idx in range(min(7, len(df.columns))):
            numeric_count = 0
            integer_count = 0
            decimal_count = 0
            total_count = 0
            sample_values = []
            
            for row_idx in range(1, min(20, len(df))):  # Skip first row, check next 19
                if pd.notna(df.iloc[row_idx, col_idx]):
                    total_count += 1
                    try:
                        val = float(df.iloc[row_idx, col_idx])
                        numeric_count += 1
                        sample_values.append(val)
                        
                        if val == int(val):
                            integer_count += 1
                        else:
                            decimal_count += 1
                    except:
                        pass
            
            if total_count > 0:
                numeric_ratio = numeric_count / total_count
                integer_ratio = integer_count / total_count if numeric_count > 0 else 0
                decimal_ratio = decimal_count / total_count if numeric_count > 0 else 0
                
                print(f"Column {col_idx}: {numeric_ratio:.1%} numeric ({integer_ratio:.1%} integers, {decimal_ratio:.1%} decimals)")
                print(f"  Sample values: {sample_values[:5]}")
        
        # Look for product-like rows (rows with alphanumeric content in first column)
        print("\nSearching for product-like rows...")
        product_candidates = []
        for idx in range(1, min(20, len(df))):  # Skip first row
            row = df.iloc[idx]
            if pd.notna(row[0]):
                first_col = str(row[0]).strip()
                # Check if first column contains alphanumeric content (potential product code)
                if any(c.isalnum() for c in first_col) and len(first_col) > 2:
                    # Check if this row has some numeric data
                    numeric_in_row = 0
                    for col_idx, val in enumerate(row[1:], 1):  # Check other columns
                        if pd.notna(val):
                            try:
                                float(val)
                                numeric_in_row += 1
                            except:
                                pass
                    
                    if numeric_in_row > 0:
                        product_candidates.append((idx, first_col, numeric_in_row))
                        print(f"Row {idx}: '{first_col[:30]}...' - {numeric_in_row} numeric columns")
        
        return df
        
    except Exception as e:
        print(f"Error analyzing Excel file: {str(e)}")
        return None

class ContainerCalculator:
    def __init__(self):
        self.container_cost_usd = 0
        self.container_volume = 0
        self.import_tax_rate = 0
        self.usd_to_ils_rate = 0
        self.rmb_to_ils_rate = 0
        self.local_transportation_ils = 0
        self.unloading_cost_ils = 0
        self.additional_fees_ils = 0
        self.products = []

    def add_product(self, name, quantity, total_volume, cost_per_unit, currency='USD'):
        self.products.append({
            'name': name,
            'quantity': quantity,
            'total_volume': total_volume,
            'volume_per_unit': total_volume / quantity if quantity > 0 else 0,
            'cost_per_unit': cost_per_unit,
            'currency': currency
        })

    def calculate_costs(self):
        total_volume = sum(p['total_volume'] for p in self.products)
        if total_volume > self.container_volume:
            raise ValueError("Total product volume exceeds container volume")
        if total_volume == 0:
            raise ValueError("Total volume cannot be zero. Please check your product data.")
        if self.usd_to_ils_rate == 0 and self.rmb_to_ils_rate == 0:
            raise ValueError("No valid exchange rate provided.")

        results = []
        total_shipping_usd = 0
        total_import_tax_ils = 0
        total_local_transportation_ils = 0
        total_unloading_ils = 0
        total_additional_fees_ils = 0
        total_cost_ils = 0

        for product in self.products:
            volume_ratio = product['total_volume'] / total_volume if total_volume > 0 else 0
            shipping_cost_usd = self.container_cost_usd * volume_ratio
            shipping_cost_per_unit_usd = shipping_cost_usd / product['quantity'] if product['quantity'] > 0 else 0

            # Determine conversion rate
            if product['currency'] == 'RMB':
                conversion_rate = self.rmb_to_ils_rate
            else:
                conversion_rate = self.usd_to_ils_rate
            if conversion_rate == 0:
                raise ValueError(f"Missing conversion rate for currency {product['currency']}")

            # Convert product cost to ILS
            original_cost_per_unit_ils = product['cost_per_unit'] * conversion_rate
            shipping_cost_per_unit_ils = shipping_cost_per_unit_usd * self.usd_to_ils_rate  # Shipping is always in USD

            # Local costs in ILS
            local_transportation_ils = self.local_transportation_ils * volume_ratio
            unloading_ils = self.unloading_cost_ils * volume_ratio
            additional_fees_ils = self.additional_fees_ils * volume_ratio

            local_transportation_per_unit_ils = local_transportation_ils / product['quantity'] if product['quantity'] > 0 else 0
            unloading_per_unit_ils = unloading_ils / product['quantity'] if product['quantity'] > 0 else 0
            additional_fees_per_unit_ils = additional_fees_ils / product['quantity'] if product['quantity'] > 0 else 0

            # Final cost per unit in ILS
            final_cost_per_unit_ils = (original_cost_per_unit_ils +
                                       shipping_cost_per_unit_ils +
                                       local_transportation_per_unit_ils +
                                       unloading_per_unit_ils +
                                       additional_fees_per_unit_ils)
            vat_per_unit_ils = final_cost_per_unit_ils * self.import_tax_rate
            final_cost_per_unit_with_vat_ils = final_cost_per_unit_ils + vat_per_unit_ils

            # Totals for this product
            total_product_cost_ils = (shipping_cost_usd * self.usd_to_ils_rate +
                                      local_transportation_ils +
                                      unloading_ils +
                                      additional_fees_ils)
            
            # Add the original product cost converted to ILS
            total_original_cost_ils = product['cost_per_unit'] * product['quantity'] * conversion_rate
            total_product_cost_ils += total_original_cost_ils

            total_shipping_usd += shipping_cost_usd
            total_import_tax_ils += vat_per_unit_ils * product['quantity']
            total_local_transportation_ils += local_transportation_ils
            total_unloading_ils += unloading_ils
            total_additional_fees_ils += additional_fees_ils
            total_cost_ils += total_product_cost_ils

            results.append({
                'name': product['name'],
                'quantity': product['quantity'],
                'total_volume': product['total_volume'],
                'volume_per_unit': product['volume_per_unit'],
                'original_cost_per_unit_ils': round(original_cost_per_unit_ils, 2),
                'shipping_cost_per_unit_ils': round(shipping_cost_per_unit_ils, 2),
                'local_transportation_per_unit_ils': round(local_transportation_per_unit_ils, 2),
                'unloading_per_unit_ils': round(unloading_per_unit_ils, 2),
                'additional_fees_per_unit_ils': round(additional_fees_per_unit_ils, 2),
                'final_cost_per_unit_ils': round(final_cost_per_unit_ils, 2),
                'final_cost_per_unit_with_vat_ils': round(final_cost_per_unit_with_vat_ils, 2),
                'vat_per_unit_ils': round(vat_per_unit_ils, 2),
                'shipping_cost_ils': round(shipping_cost_usd * self.usd_to_ils_rate, 2),
                'local_transportation_ils': round(local_transportation_ils, 2),
                'unloading_cost_ils': round(unloading_ils, 2),
                'additional_fees_ils': round(additional_fees_ils, 2),
                'total_cost_ils': round(total_product_cost_ils, 2),
                'currency': product['currency']
            })

        # Add totals row
        total_quantity = sum(p['quantity'] for p in self.products)
        results.append({
            'name': 'TOTALS',
            'quantity': total_quantity,
            'total_volume': total_volume,
            'volume_per_unit': total_volume / total_quantity if total_quantity > 0 else 0,
            'original_cost_per_unit_ils': 0,
            'shipping_cost_per_unit_ils': 0,
            'local_transportation_per_unit_ils': 0,
            'unloading_per_unit_ils': 0,
            'additional_fees_per_unit_ils': 0,
            'final_cost_per_unit_ils': 0,
            'final_cost_per_unit_with_vat_ils': 0,
            'vat_per_unit_ils': 0,
            'shipping_cost_ils': round(total_shipping_usd * self.usd_to_ils_rate, 2),
            'local_transportation_ils': round(total_local_transportation_ils, 2),
            'unloading_cost_ils': round(total_unloading_ils, 2),
            'additional_fees_ils': round(total_additional_fees_ils, 2),
            'total_cost_ils': round(total_cost_ils, 2),
            'is_total': True,
            'currency': ''
        })

        return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/static/icon-192.png')
def icon_192():
    return send_from_directory('static', 'icon-192.png')

@app.route('/static/icon-512.png')
def icon_512():
    return send_from_directory('static', 'icon-512.png')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'לא נבחר קובץ'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'לא נבחר קובץ'}), 400
    
    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({'error': 'הקובץ חייב להיות בפורמט אקסל (.xls או .xlsx)'}), 400
    
    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"\nReading Excel file: {filename}")
        
        # First, analyze the file structure
        df = analyze_excel_structure(filepath)
        if df is None:
            return jsonify({'error': 'שגיאה בקריאת קובץ אקסל'}), 500
        
        # Process the data using the DataFrame from analyze_excel_structure
        result = process_excel_data(df)
        
        # Clean up
        os.remove(filepath)
        
        # Format the response with a more informative message
        total_products = len(result['products'])
        if total_products > 0:
            message = f"הקובץ עובד בהצלחה! נמצאו {total_products} מוצרים."
        else:
            message = "לא נמצאו מוצרים תקינים בקובץ. אנא בדוק את פורמט הקובץ."
        
        response = {
            'message': message,
            'products': result['products'],
            'columns_found': result['columns_found'],
            'total_products': total_products
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'שגיאה בעיבוד הקובץ: {str(e)}'}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    """Calculate shipping costs and display results."""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'לא סופקו נתונים'}), 400

        # Extract values from JSON data
        container_cost = float(data['container_cost_usd'])
        container_volume = float(data['container_volume'])
        import_tax_rate = float(data['import_tax_rate'])
        usd_to_ils_rate = float(data['usd_to_ils_rate'])
        rmb_to_ils_rate = float(data.get('rmb_to_ils_rate', 0))
        local_transportation = float(data.get('local_transportation_ils', 0))
        unloading_cost = float(data.get('unloading_cost_ils', 0))
        additional_fees = float(data.get('additional_fees_ils', 0))
        products = data['products']

        if not products:
            return jsonify({'error': 'לא נמצאו מוצרים'}), 400

        # Initialize calculator
        calculator = ContainerCalculator()
        calculator.container_cost_usd = container_cost
        calculator.container_volume = container_volume
        calculator.import_tax_rate = import_tax_rate
        calculator.usd_to_ils_rate = usd_to_ils_rate
        calculator.rmb_to_ils_rate = rmb_to_ils_rate
        calculator.local_transportation_ils = local_transportation
        calculator.unloading_cost_ils = unloading_cost
        calculator.additional_fees_ils = additional_fees

        # Add products to calculator
        for product in products:
            calculator.add_product(
                name=product.get('name') or product.get('item'),
                quantity=int(product['quantity']),
                total_volume=float(product['total_volume']),
                cost_per_unit= float(product['cost_per_unit_usd']) if 'cost_per_unit_usd' in product else float(product['price']),
                currency=product.get('currency', 'USD')
            )

        # Calculate costs
        results = calculator.calculate_costs()

        return jsonify({
            'results': results,
            'summary': {
                'total_volume': f"{sum(p['total_volume'] for p in products):.3f}",
                'total_cost_usd': f"${sum(p['quantity'] * (p.get('cost_per_unit_usd', p.get('price', 0))) for p in products):.2f}",
                'container_cost': f"${container_cost:.2f}",
                'local_transportation': f"₪{local_transportation:.2f}",
                'unloading_cost': f"₪{unloading_cost:.2f}",
                'additional_fees': f"₪{additional_fees:.2f}"
            }
        })

    except KeyError as e:
        return jsonify({'error': f'שדה חסר: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'אירעה שגיאה: {str(e)}'}), 500

@app.route('/get-exchange-rate', methods=['GET'])
def get_exchange_rate():
    """Fetch the latest USD/ILS exchange rate from a reliable API."""
    try:
        # Try multiple APIs for reliability
        apis = [
            {
                'url': 'https://api.exchangerate-api.com/v4/latest/USD',
                'extract': lambda data: data['rates']['ILS']
            },
            {
                'url': 'https://open.er-api.com/v6/latest/USD',
                'extract': lambda data: data['rates']['ILS']
            },
            {
                'url': 'https://api.frankfurter.app/latest?from=USD&to=ILS',
                'extract': lambda data: data['rates']['ILS']
            }
        ]
        
        for api in apis:
            try:
                response = requests.get(api['url'], timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    rate = api['extract'](data)
                    return jsonify({
                        'success': True,
                        'rate': round(rate, 4),
                        'timestamp': datetime.now().isoformat(),
                        'source': api['url']
                    })
            except Exception as e:
                print(f"API {api['url']} failed: {str(e)}")
                continue
        
        # If all APIs fail, return a fallback rate (you can update this manually)
        fallback_rate = 3.65  # Approximate current rate
        return jsonify({
            'success': False,
            'rate': fallback_rate,
            'message': 'לא ניתן לקבל שער עדכני, מוצג שער ברירת מחדל',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'שגיאה בקבלת שער חליפין: {str(e)}',
            'rate': 3.65  # Fallback rate
        }), 500

@app.route('/get-currency-rates', methods=['GET'])
def get_currency_rates():
    """Fetch multiple currency exchange rates for the converter."""
    try:
        # Try to get rates from a comprehensive API
        apis = [
            {
                'url': 'https://api.exchangerate-api.com/v4/latest/USD',
                'extract': lambda data: {
                    'USD_ILS': data['rates']['ILS'],
                    'USD_CNY': data['rates']['CNY']
                }
            },
            {
                'url': 'https://open.er-api.com/v6/latest/USD',
                'extract': lambda data: {
                    'USD_ILS': data['rates']['ILS'],
                    'USD_CNY': data['rates']['CNY']
                }
            }
        ]
        
        for api in apis:
            try:
                response = requests.get(api['url'], timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    rates = api['extract'](data)
                    
                    # Calculate CNY/ILS rate (USD/ILS / USD/CNY)
                    cny_ils_rate = rates['USD_ILS'] / rates['USD_CNY']
                    cny_usd_rate = 1 / rates['USD_CNY']  # Convert USD/CNY to CNY/USD
                    
                    return jsonify({
                        'success': True,
                        'rates': {
                            'USD_ILS': round(rates['USD_ILS'], 4),
                            'CNY_USD': round(cny_usd_rate, 4),
                            'CNY_ILS': round(cny_ils_rate, 4)
                        },
                        'timestamp': datetime.now().isoformat(),
                        'source': api['url']
                    })
            except Exception as e:
                print(f"API {api['url']} failed: {str(e)}")
                continue
        
        # Fallback rates if all APIs fail
        fallback_rates = {
            'USD_ILS': 3.65,
            'CNY_USD': 0.14,
            'CNY_ILS': 0.51
        }
        
        return jsonify({
            'success': False,
            'rates': fallback_rates,
            'message': 'לא ניתן לקבל שערים עדכניים, מוצגים שערי ברירת מחדל',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'שגיאה בקבלת שערי חליפין: {str(e)}',
            'rates': {
                'USD_ILS': 3.65,
                'CNY_USD': 0.14,
                'CNY_ILS': 0.51
            }
        }), 500

# --- BEGIN: Robust Excel Extraction Logic (from analyze_excel.py) ---
def find_header_and_columns(df):
    # Strict quantity keywords
    strict_quantity_keywords = ['quantity', 'qty', 'pcs', 'pieces', 'units', 'sets/ctn', 'ctn']
    header_keywords = {
        'item': ['item', 'code', 'product', 'customer id', 'item no', 'item number', 'product code', 'sku'],
        'description': ['description', 'desc', 'product description', 'name', 'product name'],
        'unit_price': ['unit price', 'unite price', 'price per unit', 'unit cost', 'rate', 'unit rate', 'price', 'exw price', 'fob price'],
        'total_amount': ['amount', 'total', 'total amount', 'total price', 'cost', 'total fob amount'],
        'cbm': ['cbm', 'volume', 'm3', 'cubic meter', 'cubic meters', 'cubic metre', 'cubic metres', 'vol', 'space', 'size', 'cbm/box', 'total cbm']
    }
    header_row_idx = None
    column_map = {}
    
    # Scan first 15 rows for header (increased from 10)
    for idx in range(min(15, len(df))):
        row = df.iloc[idx]
        for col_idx, val in enumerate(row):
            if pd.isna(val):
                continue
            val_str = str(val).strip().lower()
            # Strict quantity matching
            if any(val_str == k for k in strict_quantity_keywords) and not any(x in val_str for x in ['price', 'amount']):
                column_map['quantity'] = col_idx
                print(f"Strict match: Found quantity column at index {col_idx}: '{val}'")
            for key, keywords in header_keywords.items():
                if key == 'quantity':
                    continue  # Already handled strictly above
                if any(k in val_str for k in keywords):
                    column_map[key] = col_idx
                    print(f"Found {key} column at index {col_idx}: '{val}'")
        # If we found at least 3 fields, treat this as header
        if len(column_map) >= 3:
            header_row_idx = idx
            print(f"Header row found at index {idx} with {len(column_map)} columns")
            break
    
    # If we didn't find enough columns, try a more aggressive search
    if header_row_idx is None or len(column_map) < 3:
        print("Trying more aggressive header search...")
        for idx in range(min(15, len(df))):
            row = df.iloc[idx]
            header_score = 0
            temp_column_map = {}
            for col_idx, val in enumerate(row):
                if pd.isna(val):
                    continue
                val_str = str(val).strip().lower()
                # Strict quantity matching
                if any(val_str == k for k in strict_quantity_keywords) and not any(x in val_str for x in ['price', 'amount']):
                    temp_column_map['quantity'] = col_idx
                # Other fields
                for key, keywords in header_keywords.items():
                    if key == 'quantity':
                        continue
                    if any(k in val_str for k in keywords):
                        temp_column_map[key] = col_idx
                if any(word in val_str for word in ['qty', 'quantity', 'pcs', 'price', 'cost', 'cbm', 'volume', 'amount', 'total']):
                    header_score += 1
            if header_score >= 2:  # At least 2 columns look like headers
                column_map = temp_column_map
                header_row_idx = idx
                print(f"Found header row at index {idx} with aggressive search: {column_map}")
                break
    
    # Find price columns (FOB or other price columns)
    if header_row_idx is not None:
        header_row = df.iloc[header_row_idx]
        for col_idx, val in enumerate(header_row):
            if pd.isna(val):
                continue
            val_str = str(val).strip().lower()
            val_str_alnum = ''.join(c if c.isalnum() else ' ' for c in val_str)
            
            # Look for any price column (FOB, EXW, etc.)
            if 'price' in val_str:
                price_col = col_idx
                print(f"Found price column at {col_idx}: '{val}'")
                break
            elif 'price' in val_str_alnum:
                price_col = col_idx
                print(f"Found price column (alnum match) at {col_idx}: '{val}'")
                break
        
        # Update column_map to use the found price column
        if 'price_col' in locals() and price_col is not None:
            column_map['unit_price'] = price_col
            print(f"Using price column {price_col} for unit_price")
        else:
            print("No price column found - will not set unit_price")
    else:
        print("No header row found - cannot detect price columns")
    
    return header_row_idx, column_map

def extract_products_from_excel(filepath):
    df = pd.read_excel(filepath, header=None)
    header_row_idx, column_map = find_header_and_columns(df)
    if header_row_idx is None:
        raise ValueError("Could not find a suitable header row.")
    
    # Check if we found the essential columns
    if 'item' not in column_map:
        # Try to find item column by looking for numeric values in first column
        print("Item column not found in headers, checking first column for item numbers...")
        item_candidates = []
        for idx in range(header_row_idx + 1, min(header_row_idx + 20, len(df))):
            if pd.notna(df.iloc[idx, 0]):
                val = str(df.iloc[idx, 0]).strip()
                # Check if it looks like an item number (numeric or alphanumeric)
                if val and (val.isdigit() or (len(val) > 1 and any(c.isdigit() for c in val))):
                    item_candidates.append((idx, val))
        
        if item_candidates:
            column_map['item'] = 0  # Use first column as item column
            print(f"Found {len(item_candidates)} potential items in first column: {[c[1] for c in item_candidates[:5]]}")
        else:
            raise ValueError("Could not find item/product column in the Excel file.")
    
    if 'quantity' not in column_map:
        raise ValueError("Could not find quantity column in the Excel file.")
    if 'unit_price' not in column_map and 'total_amount' not in column_map:
        raise ValueError("Could not find price or amount column in the Excel file.")
    
    print(f"Found columns: {column_map}")
    
    # Determine currency type for price column
    price_currency = 'USD'
    if 'unit_price' in column_map:
        header_row = df.iloc[header_row_idx]
        price_header = str(header_row[column_map['unit_price']]).strip()
        # Check if header contains 'RMB' or 'rmb' (case-insensitive)
        if 'rmb' in price_header.lower():
            price_currency = 'RMB'
            print(f"Detected RMB currency from header: '{price_header}'")
        elif 'usd' in price_header.lower() or '$' in price_header:
            price_currency = 'USD'
            print(f"Detected USD currency from header: '{price_header}'")
        else:
            print(f"No specific currency detected in header: '{price_header}', defaulting to USD")
    
    products = []
    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]
        item_val = row[column_map['item']] if 'item' in column_map else None
        if pd.isna(item_val) or (isinstance(item_val, str) and 'total' in item_val.lower()):
            break
        
        # Extract values with better error handling
        try:
            quantity = float(row[column_map['quantity']]) if 'quantity' in column_map and pd.notna(row[column_map['quantity']]) else 0
            cbm = float(row[column_map['cbm']]) if 'cbm' in column_map and pd.notna(row[column_map['cbm']]) else 0
            description = str(row[column_map['description']]).strip() if 'description' in column_map and pd.notna(row[column_map['description']]) else ''
            
            # Handle price/amount extraction
            unit_price = 0
            if 'unit_price' in column_map and pd.notna(row[column_map['unit_price']]):
                unit_price = float(row[column_map['unit_price']])
                print(f"Found unit price: {unit_price}")
            elif 'total_amount' in column_map and pd.notna(row[column_map['total_amount']]):
                total_amount = float(row[column_map['total_amount']])
                if quantity > 0:
                    unit_price = total_amount / quantity
                    print(f"Found total amount: {total_amount}, calculated unit price: {unit_price:.2f}")
                else:
                    unit_price = total_amount  # If no quantity, treat as unit price
                    print(f"No quantity found, treating amount as unit price: {unit_price}")
            
            product = {
                'item': str(item_val).strip() if item_val is not None else '',
                'description': description,
                'price': unit_price,
                'quantity': quantity,
                'cbm': cbm,
                'currency': price_currency
            }
            
            # Only add product if it has valid data
            if product['item'] and (quantity > 0 or unit_price > 0):
                products.append(product)
                print(f"Added product: {product['item']} - Qty: {quantity}, Unit Price: {unit_price:.2f}, CBM: {cbm}, Currency: {price_currency}")
            
        except (ValueError, TypeError) as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    print(f"Total products extracted: {len(products)}")
    return products
# --- END: Robust Excel Extraction Logic ---

@app.route('/upload-robust', methods=['POST'])
def upload_file_robust():
    if 'file' not in request.files:
        return jsonify({'error': 'לא נבחר קובץ'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'לא נבחר קובץ'}), 400
    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({'error': 'הקובץ חייב להיות בפורמט אקסל (.xls או .xlsx)'}), 400
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            products = extract_products_from_excel(filepath)
            message = f"הקובץ עובד בהצלחה! נמצאו {len(products)} מוצרים. (שיטה רובסטית)"
            response = {'message': message, 'products': products, 'total_products': len(products)}
        except Exception as e:
            response = {'error': f'שגיאה בעיבוד הקובץ: {str(e)}'}
        os.remove(filepath)
        return jsonify(response)
    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'שגיאה בעיבוד הקובץ: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 
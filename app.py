from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
from datetime import datetime
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
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
    Find the header row and identify the columns for Item NO., QTY(PCS), PRICE, and CBM.
    Returns a dictionary with column indices.
    """
    print("\nSearching for header row...")
    
    # Search for the header row
    header_row_idx = None
    for idx, row in df.iterrows():
        if pd.notna(row[0]) and str(row[0]).strip().startswith('Item NO.'):
            header_row_idx = idx
            print(f"Found header row at index {idx}")
            print("Header row contents:")
            for col_idx, value in enumerate(row):
                if pd.notna(value):
                    print(f"Column {col_idx}: {value}")
            break
    
    if header_row_idx is None:
        print("Could not find header row starting with 'Item NO.'")
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
    
    # Search for each column
    for col_idx, value in enumerate(header_row):
        if pd.isna(value):
            continue
            
        value = str(value).strip().upper()
        
        # Look for quantity column
        if 'QTY' in value or '(PCS)' in value:
            column_indices['quantity'] = col_idx
            print(f"Found quantity column at {col_idx}: {value}")
            
        # Look for price column
        elif 'PRICE' in value:
            column_indices['price'] = col_idx
            print(f"Found price column at {col_idx}: {value}")
            
        # Look for volume column
        elif 'CBM' in value:
            column_indices['volume'] = col_idx
            print(f"Found volume column at {col_idx}: {value}")
    
    # Verify we found all required columns
    missing_columns = [col for col, idx in column_indices.items() if idx is None]
    if missing_columns:
        print(f"Warning: Could not find columns for: {', '.join(missing_columns)}")
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
    
    # Find the header row
    header_row_idx = None
    for idx, row in df.iterrows():
        if pd.notna(row[0]) and str(row[0]).strip().startswith('Item NO.'):
            header_row_idx = idx
            print(f"Found header row at index {idx}")
            break
    
    if header_row_idx is None:
        print("Could not find header row starting with 'Item NO.'")
        return None, None
    
    # Start row is the next row after the header
    start_row = header_row_idx + 1
    print(f"Product data starts at row {start_row}")
    
    # Find the end row by looking for the first row without a product code
    end_row = None
    for idx, row in df.iloc[start_row:].iterrows():
        # Skip empty rows
        if row.isna().all():
            continue
            
        # Check if the first column contains a product code
        first_col = str(row[0]).strip() if pd.notna(row[0]) else ''
        if not first_col or not any(c.isalnum() for c in first_col):  # No alphanumeric characters means no product code
            end_row = idx - 1
            print(f"Found end of products at row {end_row}")
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
    """Analyze the Excel file structure to understand its format."""
    try:
        # Read all sheets
        xls = pd.ExcelFile(filepath)
        print(f"\nExcel file contains {len(xls.sheet_names)} sheets: {xls.sheet_names}")
        
        # Read each sheet
        for sheet_name in xls.sheet_names:
            print(f"\nAnalyzing sheet: {sheet_name}")
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            
            # Print basic information
            print(f"Number of rows: {len(df)}")
            print(f"Number of columns: {len(df.columns)}")
            print("\nColumn names:")
            for col in df.columns:
                print(f"- {col}")
            
            # Print first few rows to understand the data structure
            print("\nFirst few rows of data:")
            print(df.head().to_string())
            
            # Look for potential product information
            print("\nLooking for product-related columns...")
            for col in df.columns:
                col_lower = str(col).lower()
                if any(term in col_lower for term in ['product', 'item', 'description', 'name', 'article']):
                    print(f"Potential product name column: {col}")
                if any(term in col_lower for term in ['qty', 'quantity', 'amount', 'units', 'pcs']):
                    print(f"Potential quantity column: {col}")
                if any(term in col_lower for term in ['volume', 'cbm', 'm3', 'cubic']):
                    print(f"Potential volume column: {col}")
                if any(term in col_lower for term in ['cost', 'price', 'usd', '$', 'value']):
                    print(f"Potential cost column: {col}")
            
            # Look for any numeric columns that might contain quantities or volumes
            print("\nNumeric columns that might contain quantities or volumes:")
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    print(f"- {col}: contains values between {df[col].min()} and {df[col].max()}")
            
            return df  # Return the first sheet's data for now
            
    except Exception as e:
        print(f"Error analyzing Excel file: {str(e)}")
        return None

class ContainerCalculator:
    def __init__(self):
        self.container_cost_usd = 0
        self.container_volume = 0
        self.import_tax_rate = 0
        self.usd_to_ils_rate = 0
        self.local_transportation_ils = 0
        self.unloading_cost_ils = 0
        self.products = []

    def add_product(self, name, quantity, total_volume, cost_per_unit_usd):
        self.products.append({
            'name': name,
            'quantity': quantity,
            'total_volume': total_volume,
            'volume_per_unit': total_volume / quantity if quantity > 0 else 0,
            'cost_per_unit_usd': cost_per_unit_usd
        })

    def calculate_costs(self):
        total_volume = sum(p['total_volume'] for p in self.products)
        if total_volume > self.container_volume:
            raise ValueError("Total product volume exceeds container volume")

        results = []
        total_shipping_usd = 0
        total_import_tax_usd = 0
        total_cost_usd = 0
        total_cost_ils = 0

        for product in self.products:
            volume_ratio = product['total_volume'] / total_volume
            shipping_cost_usd = self.container_cost_usd * volume_ratio
            shipping_cost_per_unit_usd = shipping_cost_usd / product['quantity'] if product['quantity'] > 0 else 0
            import_tax_usd = shipping_cost_usd * self.import_tax_rate
            # Total cost is just shipping + import tax
            total_product_cost_usd = shipping_cost_usd + import_tax_usd
            total_product_cost_ils = total_product_cost_usd * self.usd_to_ils_rate

            total_shipping_usd += shipping_cost_usd
            total_import_tax_usd += import_tax_usd
            total_cost_usd += total_product_cost_usd
            total_cost_ils += total_product_cost_ils

            results.append({
                'name': product['name'],
                'quantity': product['quantity'],
                'total_volume': product['total_volume'],
                'volume_per_unit': product['volume_per_unit'],
                'shipping_cost_per_unit_usd': round(shipping_cost_per_unit_usd, 2),
                'shipping_cost_usd': round(shipping_cost_usd, 2),
                'import_tax_usd': round(import_tax_usd, 2),
                'total_cost_usd': round(total_product_cost_usd, 2),
                'total_cost_ils': round(total_product_cost_ils, 2)
            })

        # Add totals row
        total_cost_ils += (self.local_transportation_ils + self.unloading_cost_ils)
        
        results.append({
            'name': 'TOTALS',
            'quantity': sum(p['quantity'] for p in self.products),
            'total_volume': total_volume,
            'volume_per_unit': total_volume / sum(p['quantity'] for p in self.products) if sum(p['quantity'] for p in self.products) > 0 else 0,
            'shipping_cost_per_unit_usd': 0,  # No per-unit shipping cost for total
            'shipping_cost_usd': round(total_shipping_usd, 2),
            'import_tax_usd': round(total_import_tax_usd, 2),
            'total_cost_usd': round(total_cost_usd, 2),
            'total_cost_ils': round(total_cost_ils, 2),
            'is_total': True
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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({'error': 'File must be Excel format'}), 400
    
    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"\nReading Excel file: {filename}")
        # Read the Excel file
        df = pd.read_excel(filepath, header=None)
        
        # Process the data
        result = process_excel_data(df)
        
        # Clean up
        os.remove(filepath)
        
        # Format the response with a more informative message
        total_products = len(result['products'])
        if total_products > 0:
            message = f"Successfully processed {total_products} products from the Excel file."
        else:
            message = "No valid products found in the Excel file. Please check the file format."
        
        response = {
            'message': message,
            'products': result['products'],
            'columns_found': result['columns_found'],
            'total_products': total_products
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    """Calculate shipping costs and display results."""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract values from JSON data
        container_cost = float(data['container_cost_usd'])
        container_volume = float(data['container_volume'])
        import_tax_rate = float(data['import_tax_rate'])
        usd_to_ils_rate = float(data['usd_to_ils_rate'])
        local_transportation = float(data.get('local_transportation_ils', 0))
        unloading_cost = float(data.get('unloading_cost_ils', 0))
        products = data['products']

        if not products:
            return jsonify({'error': 'No products found'}), 400

        # Initialize calculator
        calculator = ContainerCalculator()
        calculator.container_cost_usd = container_cost
        calculator.container_volume = container_volume
        calculator.import_tax_rate = import_tax_rate
        calculator.usd_to_ils_rate = usd_to_ils_rate
        calculator.local_transportation_ils = local_transportation
        calculator.unloading_cost_ils = unloading_cost

        # Add products to calculator
        for product in products:
            calculator.add_product(
                name=product['name'],
                quantity=int(product['quantity']),
                total_volume=float(product['total_volume']),
                cost_per_unit_usd=float(product['cost_per_unit_usd'])
            )

        # Calculate costs
        results = calculator.calculate_costs()

        return jsonify({
            'results': results,
            'summary': {
                'total_volume': f"{sum(p['total_volume'] for p in products):.3f}",
                'total_cost_usd': f"${sum(p['quantity'] * p['cost_per_unit_usd'] for p in products):.2f}",
                'container_cost': f"${container_cost:.2f}",
                'local_transportation': f"₪{local_transportation:.2f}",
                'unloading_cost': f"₪{unloading_cost:.2f}"
            }
        })

    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 
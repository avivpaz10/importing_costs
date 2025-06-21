import pandas as pd

def analyze_rmb_excel():
    df = pd.read_excel('RMB-Ofer MIX 40HQ.xls', header=None)
    
    print("First 10 rows:")
    print(df.head(10).to_string())
    
    print("\n" + "="*50)
    print("Price-related headers found:")
    print("="*50)
    
    for idx, row in df.head(15).iterrows():
        for col_idx, val in enumerate(row):
            if pd.notna(val):
                val_str = str(val).strip().lower()
                if any(term in val_str for term in ['price', 'fob', 'rmb', 'amount', 'cost', 'unit']):
                    print(f'Row {idx}, Col {col_idx}: "{val}"')
    
    print("\n" + "="*50)
    print("Sample data rows (rows 5-10):")
    print("="*50)
    
    for idx in range(5, min(11, len(df))):
        row = df.iloc[idx]
        print(f"Row {idx}: {[str(val)[:20] if pd.notna(val) else 'NaN' for val in row[:10]]}")

if __name__ == "__main__":
    analyze_rmb_excel() 
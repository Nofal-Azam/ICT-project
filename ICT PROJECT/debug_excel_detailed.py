import pandas as pd
import os

def debug_excel_completely():
    print("🔍 COMPLETE EXCEL DEBUG SCRIPT")
    print("=" * 60)
    
    excel_path = "data/Book 3 final.xlsx"
    
    # Check if file exists
    if not os.path.exists(excel_path):
        print("❌ File not found at:", excel_path)
        print("Current working directory:", os.getcwd())
        print("Files in current directory:", os.listdir('.'))
        if os.path.exists('data'):
            print("Files in data folder:", os.listdir('data'))
        else:
            print("❌ 'data' folder doesn't exist!")
        return
    
    print(f"✅ File found: {excel_path}")
    print(f"File size: {os.path.getsize(excel_path)} bytes")
    
    try:
        # Get all sheet names
        excel_file = pd.ExcelFile(excel_path)
        print(f"📊 All sheets in file: {excel_file.sheet_names}")
        
        # Check each sheet in detail
        for sheet_name in excel_file.sheet_names:
            print(f"\n" + "="*60)
            print(f"📄 ANALYZING SHEET: '{sheet_name}'")
            print("="*60)
            
            # Read the sheet without any processing
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            print(f"Shape: {df.shape} (rows: {df.shape[0]}, columns: {df.shape[1]})")
            print(f"Column names: {list(df.columns)}")
            
            # Show detailed column info
            print("\n📋 COLUMN DETAILS:")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}. '{col}' (dtype: {df[col].dtype})")
            
            # Show first 5 rows with all data
            print("\n📊 FIRST 5 ROWS (RAW DATA):")
            print(df.head(5))
            
            # Show non-empty rows count
            non_empty_rows = df.dropna(how='all').shape[0]
            print(f"\nNon-empty rows: {non_empty_rows}")
            
            # Check if there are any merged cells or headers
            print(f"\nFirst cell value: '{df.iloc[0,0] if df.shape[0] > 0 else 'Empty'}'")
            
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_excel_completely()
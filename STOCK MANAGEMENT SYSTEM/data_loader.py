import pandas as pd
# --- THIS IS THE NEW IMPORT ---
from openpyxl import load_workbook
# --- END OF NEW IMPORT ---


def load_transactions_from_excel(file_path):
    """
    Load transaction data from Excel file - FIXED for your specific format
    """
    try:
        # Read the transactions sheet, skip the first row (header title)
        df = pd.read_excel(file_path, sheet_name='Sheet1', skiprows=1)
        
        print("✅ Successfully loaded transactions data!")
        
        # Clean the data - remove empty rows
        df = df.dropna(subset=['Company Symbol'])
        
        # Convert quantity and price to numeric (handle any text values)
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        df['Price Per Share (pkr)'] = pd.to_numeric(df['Price Per Share (pkr)'], errors='coerce')
        
        # Force the Total Amount column to be numeric, handling errors
        # This prevents crashes if a 'null' value is saved from the form
        if 'Total Amount(pkr)' in df.columns:
            df['Total Amount(pkr)'] = pd.to_numeric(df['Total Amount(pkr)'], errors='coerce')
        
        # We drop rows where EITHER Quantity or Price is invalid.
        df = df.dropna(subset=['Quantity', 'Price Per Share (pkr)'])
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading transactions: {e}")
        return None

def load_portfolio_from_excel(file_path):
    """
    Load portfolio summary from Excel file - FIXED for your specific format
    This file is used as a TEMPLATE for prices and company names.
    """
    try:
        # Read the portfolio sheet, skip the first row (header title)
        df = pd.read_excel(file_path, sheet_name='Sheet2', skiprows=1)
        
        print("✅ Successfully loaded portfolio template data!")
        
        # Clean the data - remove empty rows
        df = df.dropna(subset=['Company Symbol'])
        
        # We only care about the Current Market Price from this file
        numeric_columns = ['Current Market Price (PKR)']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # We only need Symbol, Name, and Price from this file
        required_cols = ['Company Symbol', 'Company Name', 'Current Market Price (PKR)']
        for col in required_cols:
            if col not in df.columns:
                print(f"❌ Error: Missing required column '{col}' in Sheet2.")
                return None
                
        return df[required_cols]
        
    except Exception as e:
        print(f"❌ Error loading portfolio: {e}")
        return None

def display_data_preview(transactions_df, portfolio_df):
    """
    Display a preview of the loaded data
    """
    print("\n" + "="*60)
    print("TRANSACTIONS DATA PREVIEW")
    print("="*60)
    if transactions_df is not None:
        print(transactions_df.head())
    else:
        print("No transactions data loaded")
    
    print("\n" + "="*60)
    print("PORTFOLIO DATA PREVIEW (FROM TEMPLATE)")
    print("="*60)
    if portfolio_df is not None:
        print(portfolio_df.head())
    else:
        print("No portfolio data loaded")

# --- THIS IS THE NEW FUNCTION ---
def save_summary_to_excel(summary_df, file_path, sheet_name="Calculated_Summary"):
    """
    Saves the calculated summary DataFrame to a specific sheet in the Excel file,
    without destroying other sheets.
    """
    try:
        # Load the existing workbook
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Write the summary dataframe to the new sheet
            # index=False means we don't save the pandas row numbers
            summary_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
    except Exception as e:
        print(f"❌ Error saving summary to Excel: {e}")
        # Re-raise the exception so the app.py can catch it
        raise
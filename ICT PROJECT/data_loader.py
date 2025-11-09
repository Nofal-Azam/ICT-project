import pandas as pd

def load_transactions_from_excel(file_path):
    """
    Load transaction data from Excel file - FIXED for your specific format
    """
    try:
        # Read the transactions sheet, skip the first row (header title)
        df = pd.read_excel(file_path, sheet_name='Sheet1', skiprows=1)
        
        print("✅ Successfully loaded transactions data!")
        print(f"Columns found: {list(df.columns)}")
        print(f"Number of transactions: {len(df)}")
        
        # Clean the data - remove empty rows
        df = df.dropna(subset=['Company Symbol'])
        
        # Convert quantity and price to numeric (handle any text values)
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        df['Price Per Share (pkr)'] = pd.to_numeric(df['Price Per Share (pkr)'], errors='coerce')
        
        # Remove any rows with invalid numeric data
        df = df.dropna(subset=['Quantity', 'Price Per Share (pkr)'])
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading transactions: {e}")
        return None

def load_portfolio_from_excel(file_path):
    """
    Load portfolio summary from Excel file - FIXED for your specific format
    """
    try:
        # Read the portfolio sheet, skip the first row (header title)
        df = pd.read_excel(file_path, sheet_name='Sheet2', skiprows=1)
        
        print("✅ Successfully loaded portfolio data!")
        print(f"Columns found: {list(df.columns)}")
        print(f"Number of portfolio items: {len(df)}")
        
        # Clean the data - remove empty rows
        df = df.dropna(subset=['Company Symbol'])
        
        # Convert numeric columns
        numeric_columns = ['Total Bought (PKR)', 'Total Sold(PKR)', 'Net Shares', 
                          'Average Buy Price(PKR)', 'Current Market Price (PKR)',
                          'Market Value (PKR)', 'Profit/Loss (PKR)']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
        
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
    print("PORTFOLIO DATA PREVIEW")
    print("="*60)
    if portfolio_df is not None:
        print(portfolio_df.head())
    else:
        print("No portfolio data loaded")
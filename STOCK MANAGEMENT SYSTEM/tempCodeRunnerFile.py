from flask import Flask, jsonify, send_from_directory, render_template, request
from portfolio import PortfolioManager
from data_loader import load_transactions_from_excel, load_portfolio_from_excel
# --- Import openpyxl ---
from openpyxl import load_workbook
# ---
# --- NEW: Import numpy ---
import numpy as np
# ---
# --- NEW: Import the calculator directly ---
from calculator import PortfolioCalculator
# ---
# --- *** THIS IS THE FIX *** ---
import pandas as pd
# ---


# Initialize Flask
app = Flask(__name__)

# --- Data Loading ---
# We must wrap data loading in a function to "refresh" it after adding a transaction.
excel_file = "data/Book 3 full final.xlsx"
transactions_df = None
portfolio_df = None
pm = None

def load_data():
    """Loads all data from the Excel file and updates global variables."""
    global transactions_df, portfolio_df, pm
    
    # 1. Load the new transactions from Sheet1
    transactions_df = load_transactions_from_excel(excel_file)
    
    # 2. Load the price list/template from Sheet2
    price_and_template_df = load_portfolio_from_excel(excel_file) 
    
    # --- THIS IS THE CRITICAL FIX ---
    # We now call our new calculator function to generate the summary
    # from scratch, using Sheet1 (transactions) and Sheet2 (prices).
    
    print("Recalculating portfolio summary from transactions...")
    
    portfolio_df = PortfolioCalculator.create_portfolio_summary(
        transactions_df, 
        price_and_template_df
    )
    
    if portfolio_df is not None:
        print("✓ Portfolio summary was successfully recalculated.")
    else:
        print("❌ ERROR: Portfolio summary calculation failed. Check data.")
        # Create an empty dataframe to avoid crashes
        portfolio_df = pd.DataFrame(columns=[
            'Company Symbol', 'Company Name', 'Total Bought (PKR)', 'Total Sold(PKR)', 
            'Net Shares', 'Average Buy Price(PKR)', 'Current Market Price (PKR)', 
            'Market Value (PKR)', 'Profit/Loss (PKR)', 'Status'
        ])
    # --- END OF FIX ---
    
    # 3. Initialize the manager with the *newly calculated* data
    pm = PortfolioManager(transactions_df, portfolio_df)
    
    print("✓ Data reloaded from Excel.")

# Load data on initial server start
load_data()


# --- Serve Frontend HTML Pages ---

@app.route("/")
def home():
    return render_template("index.html") 

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/index2_seeinvestments')
def see_investments():
    return render_template('index2_seeinvestment.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

# --- NEW: Route to serve the "Add Stock" page ---
@app.route('/add_stock')
def add_stock_page():
    return render_template('add_stock.html')


# --- API Endpoints ---

@app.route("/summary")
def summary():
    # FIX: Convert all NumPy-derived financial totals to standard Python float() 
    # to prevent "TypeError: Object of type int64 is not JSON serializable".
    
    # We use the global, recalculated dataframes
    total_investment = 0.0
    total_sales = 0.0
    portfolio_value = 0.0
    net_profit_loss = 0.0

    if transactions_df is not None:
        total_investment = float(PortfolioCalculator.calculate_total_investment(transactions_df))
        total_sales = float(PortfolioCalculator.calculate_total_sales(transactions_df))
    
    if portfolio_df is not None:
        portfolio_value = float(PortfolioCalculator.calculate_portfolio_value(portfolio_df))
        net_profit_loss = float(PortfolioCalculator.calculate_net_profit_loss(portfolio_df))

    return jsonify({
        "total_investment": total_investment,
        "total_sales": total_sales,
        "portfolio_value": portfolio_value,
        "net_profit_loss": net_profit_loss
    })

@app.route("/holdings")
def holdings():
    # This endpoint now returns the *recalculated* portfolio_df from load_data()
    
    # Handle case where portfolio is empty
    if portfolio_df is None or portfolio_df.empty:
        return jsonify([])

    # --- FINAL FIX FOR int64 ERROR ---
    # 1. Replace NaN with None (for JSON null)
    df_clean = portfolio_df.replace({np.nan: None})
    
    # 2. Convert DataFrame to a list of dicts
    records = df_clean.to_dict(orient="records")
    
    # 3. Manually convert all numpy types to python types
    clean_records = []
    for record in records:
        clean_record = {}
        for key, value in record.items():
            if isinstance(value, (np.int64, np.int32, np.int16)):
                clean_record[key] = int(value)
            elif isinstance(value, (np.float64, np.float32)):
                clean_record[key] = float(value)
            elif pd.isna(value):
                clean_record[key] = None
            else:
                clean_record[key] = value
        clean_records.append(clean_record)
    
    return jsonify(clean_records)
    # --- END OF FIX ---

# --- NEW: API Endpoint to handle adding a transaction ---
@app.route("/api/add_transaction", methods=['POST'])
def add_transaction():
    try:
        data = request.json
        print(f"Received data: {data}")

        # --- Logic to write to the Excel file ---
        
        # 1. Load the workbook
        wb = load_workbook(excel_file)
        
        # 2. Get the "PSX Transactions" sheet (assuming it's 'Sheet1')
        ws = wb['Sheet1'] 
        
        # 3. Create the new row list from the 'data' object.
        #    Ensure the order matches your Excel columns
        new_row = [
            data['date'],
            data['symbol'],
            data['companyName'],
            data['transactionType'],
            data['quantity'],
            data['price'],
            data['totalAmount'],
            data['remarks']
        ]
        
        # 4. Append the new row
        ws.append(new_row)
        
        # 5. Save the workbook
        wb.save(excel_file)
        
        # --- IMPORTANT ---
        # Now that the file is saved, we re-run all calculations.
        
        # This function re-reads the Excel file and re-populates all variables
        load_data()

        # If all went well, send success
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error adding transaction: {e}")
        import traceback
        traceback.print_exc()
        # Send a specific error back to the frontend
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/top-performers")
def top_performers():
    # This uses the global portfolio_df, which is now recalculated
    top = PortfolioCalculator.get_top_performers(portfolio_df)
    
    if top is not None:
        data = top.replace({np.nan: None})
        return data.to_dict(orient="records")
    return jsonify([])

@app.route("/company/<symbol>")
def company(symbol):
    # This uses the global portfolio_df, which is now recalculated
    data = PortfolioCalculator.get_company_analysis(portfolio_df, symbol)
    
    if not data:
        return jsonify({})

    # --- THIS IS THE NEW FIX ---
    # Loop through the dictionary and cast all numpy types to standard python types
    clean_data = {}
    for key, value in data.items():
        if isinstance(value, (np.int64, np.int32, np.int16)):
            clean_data[key] = int(value)  # Cast int64 to python int
        elif isinstance(value, (np.float64, np.float32)):
            clean_data[key] = float(value) # Cast float64 to python float
        elif pd.isna(value):
            clean_data[key] = None         # Handle NaN
        else:
            clean_data[key] = value
    # --- END OF FIX ---
    
    return jsonify(clean_data)

@app.route("/transactions")
def transactions():
    # This just uses the transactions_df, which is fine
    if transactions_df is None:
        return jsonify({})
    return jsonify(PortfolioCalculator.analyze_transactions_by_company(transactions_df) or {})

# Run Flask
if __name__ == "__main__":
    app.run(debug=True)
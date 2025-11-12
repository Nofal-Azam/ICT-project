from flask import Flask, jsonify, send_from_directory, render_template
from portfolio import PortfolioManager
from data_loader import load_transactions_from_excel, load_portfolio_from_excel

# Initialize Flask
app = Flask(__name__)

# Load Excel data (use your existing data loader)
excel_file = "data/Book 3 full final.xlsx"
transactions_df = load_transactions_from_excel(excel_file)
portfolio_df = load_portfolio_from_excel(excel_file)
pm = PortfolioManager(transactions_df, portfolio_df)

# Serve the frontend HTML
@app.route("/")
def home():
    return render_template("index.html") 

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/index2_seeinvestments')
def see_investments():
    return render_template('index2_seeinvestment.html')

# API Endpoints

@app.route("/summary")
def summary():
    # FIX: Convert all NumPy-derived financial totals to standard Python float() 
    # to prevent "TypeError: Object of type int64 is not JSON serializable".
    return jsonify({
        "total_investment": float(pm.calculator.calculate_total_investment(transactions_df)),
        "total_sales": float(pm.calculator.calculate_total_sales(transactions_df)),
        "portfolio_value": float(pm.calculator.calculate_portfolio_value(portfolio_df)),
        "net_profit_loss": float(pm.calculator.calculate_net_profit_loss(portfolio_df))
    })

@app.route("/holdings")
def holdings():
    # pandas to_dict(orient="records") usually handles NumPy types, so no change is needed here.
    return portfolio_df.to_dict(orient="records")

@app.route("/top-performers")
def top_performers():
    top = pm.calculator.get_top_performers(portfolio_df)
    # Ensure any NumPy types are handled if to_dict doesn't convert them correctly.
    # The dataframe to_dict method is generally fine for this, so leaving it as is.
    if top is not None:
        return top.to_dict(orient="records")
    return jsonify([])

@app.route("/company/<symbol>")
def company(symbol):
    data = pm.calculator.get_company_analysis(portfolio_df, symbol)
    # Ensure any NumPy types within 'data' are standard Python types if possible
    # before returning the JSON. If the data structure is a simple dictionary, 
    # you might need casting inside the get_company_analysis method.
    return jsonify(data or {})

@app.route("/transactions")
def transactions():
    # If analyze_transactions_by_company returns a dictionary with NumPy values, 
    # those values would also need to be cast to float/int.
    return jsonify(pm.calculator.analyze_transactions_by_company(transactions_df) or {})

# Run Flask
if __name__ == "__main__":
    app.run(debug=True)
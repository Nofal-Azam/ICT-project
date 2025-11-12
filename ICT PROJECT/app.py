from flask import Flask, jsonify, send_from_directory,render_template
from portfolio import PortfolioManager
from data_loader import load_transactions_from_excel, load_portfolio_from_excel

# Initialize Flask
app = Flask(__name__)

# Load Excel data (use your existing data loader)
excel_file = "Book 3 full final.xlsx"
transactions_df = load_transactions_from_excel(excel_file)
portfolio_df = load_portfolio_from_excel(excel_file)
pm = PortfolioManager(transactions_df, portfolio_df)

# Serve the frontend HTML
@app.route("/")
def home():
    return render_template('index.html')  # assumes index.html in same folder

# API Endpoints

@app.route("/summary")
def summary():
    return jsonify({
        "total_investment": pm.calculator.calculate_total_investment(transactions_df),
        "total_sales": pm.calculator.calculate_total_sales(transactions_df),
        "portfolio_value": pm.calculator.calculate_portfolio_value(portfolio_df),
        "net_profit_loss": pm.calculator.calculate_net_profit_loss(portfolio_df)
    })

@app.route("/holdings")
def holdings():
    return portfolio_df.to_dict(orient="records")

@app.route("/top-performers")
def top_performers():
    top = pm.calculator.get_top_performers(portfolio_df)
    if top is not None:
        return top.to_dict(orient="records")
    return jsonify([])

@app.route("/company/<symbol>")
def company(symbol):
    data = pm.calculator.get_company_analysis(portfolio_df, symbol)
    return jsonify(data or {})

@app.route("/transactions")
def transactions():
    return jsonify(pm.calculator.analyze_transactions_by_company(transactions_df) or {})

@app.route('/seeinvestment')
def see_investment():
    return render_template('index2_seeinvestment.html')

# Run Flask
if __name__ == "__main__":
    app.run(debug=True)

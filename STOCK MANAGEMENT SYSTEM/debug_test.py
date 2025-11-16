# This script tests the entire data pipeline from end-to-end.

import os
from data_loader import load_transactions_from_excel, load_portfolio_from_excel
from calculator import PortfolioCalculator

# --- Configuration ---
excel_file = "data/Book 3 full final.xlsx"
# ---

def run_debug_test():
    print("="*60)
    print("🚀 RUNNING END-TO-END DATA PIPELINE TEST 🚀")
    print("="*60)

    # 1. Check if file exists
    if not os.path.exists(excel_file):
        print(f"❌ FATAL ERROR: File not found at {excel_file}")
        return
    print(f"✅ File found: {excel_file}")

    # 2. Load data using our data_loader
    print("\n--- STEP 1: LOADING DATA ---")
    transactions_df = load_transactions_from_excel(excel_file)
    price_template_df = load_portfolio_from_excel(excel_file)

    if transactions_df is None or price_template_df is None:
        print("❌ FATAL ERROR: Failed to load data. See errors above.")
        return
    
    print("✅ Transactions and Price Template loaded successfully.")

    # 3. Run the new calculation function
    print("\n--- STEP 2: RECALCULATING SUMMARY ---")
    try:
        portfolio_summary_df = PortfolioCalculator.create_portfolio_summary(
            transactions_df,
            price_template_df
        )
        if portfolio_summary_df is None or portfolio_summary_df.empty:
            print("❌ FATAL ERROR: Calculation returned an empty summary.")
            return
        
        print("✅ Portfolio Summary Recalculated Successfully!")

    except Exception as e:
        print(f"❌ FATAL ERROR during calculation: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Display the final result
    print("\n--- STEP 3: FINAL CALCULATED SUMMARY ---")
    print("="*60)
    print(portfolio_summary_df.to_string()) # .to_string() prints all rows
    print("="*60)
    print("✅ TEST COMPLETE. If the summary above looks correct, all backend logic is working.")

if __name__ == "__main__":
    run_debug_test()
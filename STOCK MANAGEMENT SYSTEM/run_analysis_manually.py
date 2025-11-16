# This is a new script you can run from your terminal
# to manually update your Excel file.
#
# To run:
# python run_analysis_manually.py
#
import os
from data_loader import (
    load_transactions_from_excel, 
    load_portfolio_from_excel, 
    save_summary_to_excel # We will add this function
)
from calculator import PortfolioCalculator

excel_file = "data/Book 3 full final.xlsx"

def run_manual_analysis():
    print("="*60)
    print("🚀 RUNNING MANUAL PORTFOLIO ANALYSIS 🚀")
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

    # 4. Save the new summary to the Excel file
    print("\n--- STEP 3: SAVING TO EXCEL ---")
    try:
        save_summary_to_excel(portfolio_summary_df, excel_file, "Calculated_Summary")
        print(f"✅ Successfully saved new summary to 'Calculated_Summary' sheet in {excel_file}")
    except Exception as e:
        print(f"❌ FATAL ERROR during saving: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE.")
    print("="*60)

if __name__ == "__main__":
    run_manual_analysis()
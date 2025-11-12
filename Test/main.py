import os
from data_loader import load_transactions_from_excel, load_portfolio_from_excel, display_data_preview
from portfolio import PortfolioManager

def main():
    """
    Main function to run the PSX Portfolio Management System
    """
    print("🚀 PSX Portfolio Management System")
    print("=" * 40)
    
    # Load data from Excel file
    excel_file = "Book 3 full final.xlsx"  # Updated file name
    
    print("📊 Loading data from Excel file...")
    
    transactions_df = load_transactions_from_excel(excel_file)
    portfolio_df = load_portfolio_from_excel(excel_file)
    
    if transactions_df is None or portfolio_df is None:
        print("❌ Failed to load data. Please check the file path and format.")
        return
    
    # Display data preview
    display_data_preview(transactions_df, portfolio_df)
    
    
    # Create portfolio manager
    portfolio_manager = PortfolioManager(transactions_df, portfolio_df)
    
    # Main menu loop
    while True:
        print("\n" + "="*50)
        print("📊 MAIN MENU")
        print("="*50)
        print("1. Portfolio Summary")
        print("2. View All Holdings") 
        print("3. Top Performers")
        print("4. Company Analysis")
        print("5. Transaction Analysis")
        print("6. Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            portfolio_manager.display_portfolio_summary()
        
        elif choice == '2':
            portfolio_manager.display_holdings()
        
        elif choice == '3':
            portfolio_manager.display_top_performers()
        
        elif choice == '4':
            symbol = input("Enter company symbol (e.g., ENGRO, LUCK): ").strip()
            portfolio_manager.get_company_details(symbol)
        
        elif choice == '5':
            portfolio_manager.display_transaction_analysis()
        
        elif choice == '6':
            print("Thank you for using PSX Portfolio Management System! 👋")
            break
        
        else:
            print("❌ Invalid choice. Please enter a number between 1-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
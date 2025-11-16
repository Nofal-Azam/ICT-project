import numpy as np
import pandas as pd

class PortfolioCalculator:
    """
    Handles all portfolio calculations - UPDATED with new create_summary function
    """
    
    # --- NEW FUNCTION ---
    # This is the new function that does the full calculation.
    @staticmethod
    def create_portfolio_summary(transactions_df, price_template_df):
        """
        Generates a fresh portfolio summary dataframe from raw transactions
        and a price template.
        """
        if transactions_df is None or transactions_df.empty:
            print("No transactions found.")
            return pd.DataFrame()
            
        if price_template_df is None or price_template_df.empty:
            print("No price template found.")
            return pd.DataFrame()

        # 1. Analyze transactions to get totals and net shares
        tx_analysis = PortfolioCalculator.analyze_transactions_by_company(transactions_df)
        
        # 2. Convert analysis dict to a DataFrame
        summary_df = pd.DataFrame.from_dict(tx_analysis, orient='index')
        summary_df.reset_index(inplace=True)
        summary_df.rename(columns={'index': 'Company Symbol'}, inplace=True)

        # 3. Merge with the price/template data from Sheet2
        # We need 'Company Name' and 'Current Market Price (PKR)' from this file.
        price_df = price_template_df[['Company Symbol', 'Company Name', 'Current Market Price (PKR)']].copy()
        
        # Ensure 'Current Market Price (PKR)' is numeric, handling potential errors
        price_df['Current Market Price (PKR)'] = pd.to_numeric(price_df['Current Market Price (PKR)'], errors='coerce').fillna(0)

        # Merge analysis with price data
        summary_df = pd.merge(summary_df, price_df, on='Company Symbol', how='left')

        # 4. Calculate final portfolio columns
        summary_df['Total Bought (PKR)'] = summary_df['total_bought']
        summary_df['Total Sold(PKR)'] = summary_df['total_sold']
        summary_df['Net Shares'] = summary_df['net_quantity']
        
        # Calculate Average Buy Price, handle division by zero
        summary_df['Average Buy Price(PKR)'] = summary_df.apply(
            lambda row: (row['total_bought'] / row['total_buy_quantity']) if row['total_buy_quantity'] > 0 else 0,
            axis=1
        )
        
        # Calculate Market Value
        summary_df['Market Value (PKR)'] = summary_df['Net Shares'] * summary_df['Current Market Price (PKR)']
        
        # Calculate Profit/Loss
        # P/L = (Current Value of Net Shares + Total Sales) - Total Investment
        summary_df['Profit/Loss (PKR)'] = (summary_df['Market Value (PKR)'] + summary_df['Total Sold(PKR)']) - summary_df['Total Bought (PKR)']

        # Calculate Status (Return %)
        summary_df['Status'] = summary_df.apply(
            lambda row: (row['Profit/Loss (PKR)'] / row['Total Bought (PKR)']) * 100 if row['Total Bought (PKR)'] > 0 else 0,
            axis=1
        )
        # Format 'Status' to match the old 'Status' column (which was P/L %)
        summary_df['Status'] = summary_df['Status'].apply(lambda x: f"{x:.2f}%")

        # 5. Clean up columns to match the exact output format
        final_columns = [
            'Company Symbol', 
            'Company Name', 
            'Total Bought (PKR)', 
            'Total Sold(PKR)', 
            'Net Shares', 
            'Average Buy Price(PKR)', 
            'Current Market Price (PKR)', 
            'Market Value (PKR)', 
            'Profit/Loss (PKR)', 
            'Status'
        ]
        
        # Add any missing columns with 0 or NaN
        for col in final_columns:
            if col not in summary_df.columns:
                summary_df[col] = 0

        return summary_df[final_columns]

    # --- END OF NEW FUNCTION ---

    @staticmethod
    def calculate_total_investment(transactions_df):
        """
        Calculate total amount invested from transactions
        """
        if transactions_df is None: return 0
        buy_transactions = transactions_df[transactions_df['Transaction Type'] == 'Buy']
        
        # Calculate total amount for buy transactions
        if 'Total Amount(pkr)' in buy_transactions.columns:
            # Use 'Total Amount(pkr)' if it's reliable (already coerced in data_loader)
            total_investment = buy_transactions['Total Amount(pkr)'].sum()
        else:
            # Calculate manually
            total_investment = (buy_transactions['Quantity'] * buy_transactions['Price Per Share (pkr)']).sum()
        
        return total_investment
    
    @staticmethod
    def calculate_total_sales(transactions_df):
        """
        Calculate total amount from sales
        """
        if transactions_df is None: return 0
        sell_transactions = transactions_df[transactions_df['Transaction Type'] == 'Sell']
        
        # Calculate total amount for sell transactions
        if 'Total Amount(pkr)' in sell_transactions.columns:
            total_sales = sell_transactions['Total Amount(pkr)'].sum()
        else:
            # Calculate manually
            total_sales = (sell_transactions['Quantity'] * sell_transactions['Price Per Share (pkr)']).sum()
        
        return total_sales
    
    @staticmethod
    def calculate_net_profit_loss(portfolio_df):
        """
        Calculate total profit/loss across all holdings
        """
        if portfolio_df is None or 'Profit/Loss (PKR)' not in portfolio_df.columns:
            return 0
        
        return portfolio_df['Profit/Loss (PKR)'].sum()
    
    @staticmethod
    def calculate_portfolio_value(portfolio_df):
        """
        Calculate total current market value of portfolio
        """
        if portfolio_df is None or 'Market Value (PKR)' not in portfolio_df.columns:
            return 0

        return portfolio_df['Market Value (PKR)'].sum()
    
    @staticmethod
    def get_top_performers(portfolio_df, top_n=3):
        """
        Get top performing stocks by profit/loss
        """
        if portfolio_df is None or len(portfolio_df) == 0:
            return None
            
        # Create a copy to avoid modifying original data
        df = portfolio_df.copy()
        
        # Note: The 'Status' column now holds the string representation, e.g., "5.50%"
        # We need to create a numeric version for sorting
        df['Profit/Loss % Numeric'] = df.apply(
            lambda row: (row['Profit/Loss (PKR)'] / row['Total Bought (PKR)']) * 100 if row['Total Bought (PKR)'] > 0 else 0,
            axis=1
        )

        # Sort by profit/loss
        top_performers = df.nlargest(top_n, 'Profit/Loss (PKR)')
        
        # Add the numeric P/L % column for display
        top_performers['Profit/Loss %'] = top_performers['Profit/Loss % Numeric']
        
        return top_performers[['Company Symbol', 'Company Name', 'Profit/Loss (PKR)', 'Profit/Loss %']]
    
    @staticmethod
    def get_company_analysis(portfolio_df, company_symbol):
        """
        Get detailed analysis for a specific company
        """
        if portfolio_df is None:
            return None
            
        company_data = portfolio_df[portfolio_df['Company Symbol'] == company_symbol.upper()]
        
        if company_data.empty:
            return None
        
        # Use .iloc[0] to get the first (and only) row's data as a dictionary
        data_dict = company_data.iloc[0].to_dict()
        
        # Remap to the expected keys
        return {
            'symbol': data_dict.get('Company Symbol'),
            'name': data_dict.get('Company Name'),
            'total_bought': data_dict.get('Total Bought (PKR)'),
            'total_sold': data_dict.get('Total Sold(PKR)'),
            'net_shares': data_dict.get('Net Shares'),
            'avg_buy_price': data_dict.get('Average Buy Price(PKR)'),
            'current_price': data_dict.get('Current Market Price (PKR)'),
            'market_value': data_dict.get('Market Value (PKR)'),
            'profit_loss': data_dict.get('Profit/Loss (PKR)'),
            'status': data_dict.get('Status', 'Unknown') # 'Status' is now the P/L % string
        }
    
    @staticmethod
    def analyze_transactions_by_company(transactions_df):
        """
        Analyze transactions by company
        """
        if transactions_df is None:
            return None
            
        analysis = {}
        
        # --- THIS IS THE CORRECTION ---
        # We create a copy to avoid modifying the original dataframe
        transactions_copy = transactions_df.copy()

        # Fill NaN 'Total Amount(pkr)' by calculating from Quantity * Price
        # This makes sure we use the most accurate total amount for every transaction
        if 'Total Amount(pkr)' in transactions_copy.columns:
            transactions_copy['Total Amount(pkr)'] = transactions_copy.apply(
                lambda row: (row['Quantity'] * row['Price Per Share (pkr)']) 
                            if (pd.isna(row['Total Amount(pkr)']) or row['Total Amount(pkr)'] == 0) 
                            else row['Total Amount(pkr)'],
                axis=1
            )
        else:
            # If the column doesn't exist at all, create it
            transactions_copy['Total Amount(pkr)'] = transactions_copy['Quantity'] * transactions_copy['Price Per Share (pkr)']
        # --- END OF CORRECTION ---

        for symbol in transactions_copy['Company Symbol'].unique():
            company_txs = transactions_copy[transactions_copy['Company Symbol'] == symbol]
            
            buy_txs = company_txs[company_txs['Transaction Type'] == 'Buy']
            sell_txs = company_txs[company_txs['Transaction Type'] == 'Sell']
            
            # Now we can safely sum the 'Total Amount(pkr)' column
            total_bought = buy_txs['Total Amount(pkr)'].sum()
            total_sold = sell_txs['Total Amount(pkr)'].sum()

            total_buy_quantity = buy_txs['Quantity'].sum()
            net_quantity = total_buy_quantity - sell_txs['Quantity'].sum()
            
            analysis[symbol] = {
                'total_bought': total_bought,
                'total_sold': total_sold,
                'net_quantity': net_quantity,
                'total_buy_quantity': total_buy_quantity, # Needed for Avg Buy Price
                'buy_count': len(buy_txs),
                'sell_count': len(sell_txs)
            }
        
        return analysis
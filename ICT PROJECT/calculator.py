class PortfolioCalculator:
    """
    Handles all portfolio calculations - UPDATED for your data
    """
    
    @staticmethod
    def calculate_total_investment(transactions_df):
        """
        Calculate total amount invested from transactions
        """
        buy_transactions = transactions_df[transactions_df['Transaction Type'] == 'Buy']
        
        # Calculate total amount for buy transactions
        if 'Total Amount(pkr)' in buy_transactions.columns:
            total_investment = buy_transactions['Total Amount(pkr)'].sum()
        else:
            # Calculate manually if formula column is text
            total_investment = (buy_transactions['Quantity'] * buy_transactions['Price Per Share (pkr)']).sum()
        
        return total_investment
    
    @staticmethod
    def calculate_total_sales(transactions_df):
        """
        Calculate total amount from sales
        """
        sell_transactions = transactions_df[transactions_df['Transaction Type'] == 'Sell']
        
        # Calculate total amount for sell transactions
        if 'Total Amount(pkr)' in sell_transactions.columns:
            total_sales = sell_transactions['Total Amount(pkr)'].sum()
        else:
            # Calculate manually if formula column is text
            total_sales = (sell_transactions['Quantity'] * sell_transactions['Price Per Share (pkr)']).sum()
        
        return total_sales
    
    @staticmethod
    def calculate_net_profit_loss(portfolio_df):
        """
        Calculate total profit/loss across all holdings
        """
        if 'Profit/Loss (PKR)' in portfolio_df.columns:
            total_pl = portfolio_df['Profit/Loss (PKR)'].sum()
        else:
            total_pl = 0
        
        return total_pl
    
    @staticmethod
    def calculate_portfolio_value(portfolio_df):
        """
        Calculate total current market value of portfolio
        """
        if 'Market Value (PKR)' in portfolio_df.columns:
            total_value = portfolio_df['Market Value (PKR)'].sum()
        else:
            total_value = 0
        
        return total_value
    
    @staticmethod
    def get_top_performers(portfolio_df, top_n=3):
        """
        Get top performing stocks by profit/loss
        """
        if portfolio_df is None or len(portfolio_df) == 0:
            return None
            
        # Create a copy to avoid modifying original data
        df = portfolio_df.copy()
        
        # Calculate profit/loss percentage if not exists
        if 'Profit/Loss %' not in df.columns and 'Total Bought (PKR)' in df.columns:
            df['Profit/Loss %'] = (df['Profit/Loss (PKR)'] / df['Total Bought (PKR)']) * 100
        
        # Sort by profit/loss
        top_performers = df.nlargest(top_n, 'Profit/Loss (PKR)')
        
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
        
        return {
            'symbol': company_data['Company Symbol'].iloc[0],
            'name': company_data['Company Name'].iloc[0],
            'total_bought': company_data['Total Bought (PKR)'].iloc[0],
            'total_sold': company_data['Total Sold(PKR)'].iloc[0],
            'net_shares': company_data['Net Shares'].iloc[0],
            'avg_buy_price': company_data['Average Buy Price(PKR)'].iloc[0],
            'current_price': company_data['Current Market Price (PKR)'].iloc[0],
            'market_value': company_data['Market Value (PKR)'].iloc[0],
            'profit_loss': company_data['Profit/Loss (PKR)'].iloc[0],
            'status': company_data['Status'].iloc[0] if 'Status' in company_data.columns else 'Unknown'
        }
    
    @staticmethod
    def analyze_transactions_by_company(transactions_df):
        """
        Analyze transactions by company
        """
        if transactions_df is None:
            return None
            
        analysis = {}
        
        for symbol in transactions_df['Company Symbol'].unique():
            company_txs = transactions_df[transactions_df['Company Symbol'] == symbol]
            
            buy_txs = company_txs[company_txs['Transaction Type'] == 'Buy']
            sell_txs = company_txs[company_txs['Transaction Type'] == 'Sell']
            
            total_bought = (buy_txs['Quantity'] * buy_txs['Price Per Share (pkr)']).sum()
            total_sold = (sell_txs['Quantity'] * sell_txs['Price Per Share (pkr)']).sum()
            net_quantity = buy_txs['Quantity'].sum() - sell_txs['Quantity'].sum()
            
            analysis[symbol] = {
                'total_bought': total_bought,
                'total_sold': total_sold,
                'net_quantity': net_quantity,
                'buy_count': len(buy_txs),
                'sell_count': len(sell_txs)
            }
        
        return analysis
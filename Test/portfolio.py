from calculator import PortfolioCalculator

class PortfolioManager:
    """
    Main portfolio management class - UPDATED for your data
    """
    
    def __init__(self, transactions_df, portfolio_df):
        self.transactions_df = transactions_df
        self.portfolio_df = portfolio_df
        self.calculator = PortfolioCalculator()
    
    def display_portfolio_summary(self):
        """
        Display overall portfolio summary
        """
        total_investment = self.calculator.calculate_total_investment(self.transactions_df)
        total_sales = self.calculator.calculate_total_sales(self.transactions_df)
        net_pl = self.calculator.calculate_net_profit_loss(self.portfolio_df)
        portfolio_value = self.calculator.calculate_portfolio_value(self.portfolio_df)
        
        print("\n" + "="*60)
        print("PORTFOLIO SUMMARY")
        print("="*60)
        print(f"Total Investment:      PKR {total_investment:,.2f}")
        print(f"Total Sales:           PKR {total_sales:,.2f}")
        print(f"Current Portfolio Value: PKR {portfolio_value:,.2f}")
        print(f"Net Profit/Loss:       PKR {net_pl:,.2f}")
        
        # Calculate overall return percentage
        if total_investment > 0:
            return_percentage = (net_pl / total_investment) * 100
            print(f"Overall Return:        {return_percentage:+.2f}%")
    
    def display_holdings(self):
        """
        Display all current holdings
        """
        print("\n" + "="*80)
        print("CURRENT HOLDINGS")
        print("="*80)
        
        if self.portfolio_df is None or len(self.portfolio_df) == 0:
            print("No portfolio data available")
            return
        
        for _, holding in self.portfolio_df.iterrows():
            profit_loss = holding.get('Profit/Loss (PKR)', 0)
            status = "📈" if profit_loss >= 0 else "📉"
            
            print(f"{status} {holding['Company Symbol']:6} | "
                  f"Shares: {holding.get('Net Shares', 0):6,.0f} | "
                  f"Avg Buy: PKR {holding.get('Average Buy Price(PKR)', 0):8.2f} | "
                  f"Current: PKR {holding.get('Current Market Price (PKR)', 0):8.2f} | "
                  f"P&L: PKR {profit_loss:10,.2f} | "
                  f"Status: {holding.get('Status', 'Unknown')}")
    
    def display_top_performers(self):
        """
        Display top performing stocks
        """
        top_performers = self.calculator.get_top_performers(self.portfolio_df)
        
        if top_performers is None or len(top_performers) == 0:
            print("No portfolio data available for analysis")
            return
        
        print("\n" + "="*60)
        print("TOP PERFORMING STOCKS")
        print("="*60)
        
        for _, stock in top_performers.iterrows():
            profit_loss = stock.get('Profit/Loss (PKR)', 0)
            emoji = "🚀" if profit_loss >= 0 else "⚠️"
            print(f"{emoji} {stock['Company Symbol']}: {stock['Company Name']}")
            print(f"   Profit/Loss: PKR {profit_loss:,.2f} "
                  f"({stock.get('Profit/Loss %', 0):+.2f}%)")
            print()
    
    def get_company_details(self, symbol):
        """
        Get detailed information for a specific company
        """
        company_data = self.calculator.get_company_analysis(self.portfolio_df, symbol.upper())
        
        if company_data:
            print(f"\n📊 COMPANY ANALYSIS: {company_data['symbol']} - {company_data['name']}")
            print("-" * 50)
            print(f"Total Invested:    PKR {company_data['total_bought']:,.2f}")
            print(f"Total Sold:        PKR {company_data['total_sold']:,.2f}")
            print(f"Net Shares:        {company_data['net_shares']:,.0f}")
            print(f"Avg Buy Price:     PKR {company_data['avg_buy_price']:.2f}")
            print(f"Current Price:     PKR {company_data['current_price']:.2f}")
            print(f"Market Value:      PKR {company_data['market_value']:,.2f}")
            print(f"Profit/Loss:       PKR {company_data['profit_loss']:,.2f}")
            print(f"Status:            {company_data['status']}")
            
            # Calculate return percentage
            if company_data['total_bought'] > 0:
                return_pct = (company_data['profit_loss'] / company_data['total_bought']) * 100
                print(f"Return:            {return_pct:+.2f}%")
        else:
            print(f"Company with symbol '{symbol}' not found in portfolio.")
    
    def display_transaction_analysis(self):
        """
        Display analysis of all transactions
        """
        company_analysis = self.calculator.analyze_transactions_by_company(self.transactions_df)
        
        if company_analysis:
            print("\n" + "="*60)
            print("TRANSACTION ANALYSIS BY COMPANY")
            print("="*60)
            
            for symbol, analysis in company_analysis.items():
                print(f"\n{symbol}:")
                print(f"  Buy Transactions: {analysis['buy_count']}")
                print(f"  Sell Transactions: {analysis['sell_count']}")
                print(f"  Total Invested: PKR {analysis['total_bought']:,.2f}")
                print(f"  Total Sales: PKR {analysis['total_sold']:,.2f}")
                print(f"  Net Shares: {analysis['net_quantity']:,.0f}")
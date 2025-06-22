import pandas as pd
import yfinance as yf
from finvizfinance.screener.overview import Overview
from datetime import datetime, timedelta
from finvizfinance.quote import finvizfinance
import pandas as pd
import dataframe_image as dfi
from matplotlib import style
from tabulate import tabulate  # Optional, for better table formatting
import os


def get_small_cap_stocks():
    """
    Fetch a list of small cap stocks.
    """
    try:
        screener = Overview()
        filters = {'Price': 'Under $50', 'Market Cap.': 'Small ($300mln to $2bln)'}
        screener.set_filter(filters_dict=filters)
        df_stocks = screener.screener_view()
        df_stocks.to_csv('small_cap_stocks.csv', index=False)  # Display the first few rows of the DataFrame for debugging
        return df_stocks
    except Exception as e:
        print(f"Error fetching stocks from Finviz: {str(e)}")
        return []
    
def get_micro_cap_stocks():
    """
    Fetch a list of microcap stocks.
    """
    try:
        screener = Overview()
        filters = {'Price': 'Under $50', 'Market Cap.': 'Micro ($50mln to $300mln)'}
        screener.set_filter(filters_dict=filters)
        df_stocks = screener.screener_view()
        df_stocks.to_csv('micro_cap_stocks.csv', index=False)  # Save to CSV for further analysis
        return df_stocks
    except Exception as e:
        print(f"Error fetching stocks from Finviz: {str(e)}")
        return []
    
def get_small_cap_stocks_any_price():
    """
    Fetch a list of small cap stocks.
    """
    try:
        screener = Overview()
        filters = {'Price': 'Any', 'Market Cap.': 'Small ($300mln to $2bln)'}
        screener.set_filter(filters_dict=filters)
        df_stocks = screener.screener_view()
        df_stocks.to_csv('small_cap_stocks.csv', index=False)  # Display the first few rows of the DataFrame for debugging
        return df_stocks
    except Exception as e:
        print(f"Error fetching stocks from Finviz: {str(e)}")
        return []

def get_micro_cap_stocks_any_price():
    """
    Fetch a list of microcap stocks.
    """
    try:
        screener = Overview()
        filters = {'Price': 'Any', 'Market Cap.': 'Micro ($50mln to $300mln)'}
        screener.set_filter(filters_dict=filters)
        df_stocks = screener.screener_view()
        df_stocks.to_csv('micro_cap_stocks.csv', index=False)  # Save to CSV for further analysis
        return df_stocks
    except Exception as e:
        print(f"Error fetching stocks from Finviz: {str(e)}")
        return []

def gainers(company_tickers): 
    """ Functions finds all small cap stock which had increased in momenentum on the day"""
    Date = [] 
    tickers_list = [] 
    company_names = [] 
    changes_list = [] 
    volumes_list = [] 
    prices_list = [] 

    for ticker, name in company_tickers: 
        if not pd.notna(ticker):  # Skip NaN values
            print(f"Skipping invalid ticker: {ticker}")

        print(f"Processing ticker: {ticker}")     
        try:
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            # Fetch historical data
            print(f"Loading data for {ticker} from {start_date} to {end_date}...")
            raw_data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
            dates = raw_data.index.strftime('%Y-%m-%d').tolist()

            df = pd.DataFrame(raw_data.values, columns=['Close', 'High', 'Low', 'Open', 'Volume'])
    
            df.insert(0, 'Date', dates)

            df['Date'] = pd.to_datetime(df['Date'])
            print("Dataframe is loading")

            df['Date'] = pd.to_datetime(df['Date'])
            print(df)
            
            if df.empty or len(df) < 2:
                print(f"Not sufficient data for {ticker}.")
                continue 

            # Ensure price is above $0.70
            if df['Close'].iloc[-1] < 0.70:
                print(f"Skipping {ticker} due to low price: {df['Close'].iloc[-1]}")
                continue

            # Check if volume is sufficient
            volumes = list(df['Volume'])
            print(volumes)
            if volumes[-1] < 1000000:
                print("Stock volume is too low")
                continue
            
            # Get close prices
            close_prices = list(df['Close'])
            print(f"Close prices for {ticker}: {close_prices}")

            # Calculate average volume for the first 4 days
            avg_vol = df['Volume'][:4].mean()
            if len(volumes) >= 2 and pd.notna(volumes[-1]) and pd.notna(volumes[-2]) and pd.notna(close_prices[-1]) and pd.notna(close_prices[-2]):
                if (volumes[-1] > avg_vol) and (close_prices[-1] > close_prices[-2]):
                    print(f"Volume increased for {ticker}: {volumes[-1]} > {avg_vol}")
                    print(f"Price increased for {ticker}: {volumes[-1]} > {volumes[-2]}")
                    Date.append(df['Date'].iloc[-1])
                    tickers_list.append(ticker)
                    company_names.append(name)
                    changes_list.append((close_prices[-1] - close_prices[-2])/close_prices[-2]*100)
                    volumes_list.append(volumes[-1])
                    prices_list.append(close_prices[-1])
                else:
                    print(f"{ticker} did not meet criteria.")
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")

    # Put data into dictionary
    data = {
        'Date': Date,
        'Ticker': tickers_list,
        'Company': company_names,
        'Price' : prices_list,
        '%Change': changes_list,
        'Volume': volumes_list,
    } 
    return pd.DataFrame(data)

def finviz_gainers(): 
    # Initialize Overview object
    foverview = Overview()

    # Set filter for stocks with positive daily change
    #filters_dict = {'Change': 'Any', 'Current Volume': 'Over 1M'}
    #filters_dict = {'Change': 'Up 10%', 'Current Volume': 'Over 1M'}
    #filters_dict = {'Change': 'Up 10%', 'Average Volume': 'Over 1M'}
    filters_dict = {'Change': 'Up 10%'}


    # Fetch the data
    foverview.set_filter(filters_dict=filters_dict)

    # Retrieve the screener data, ordering by Change
    df = foverview.screener_view(order='Change')
    df['%Change'] = df['Change']*100 

    # Sort the DataFrame by 'Change' in descending order
    #df['Change'] = df['Change'].str.rstrip('%').astype(float)  # Convert percentage strings to float
    df = df.sort_values(by='Change', ascending=False)

    # Display the results
    return df[['Ticker', 'Company', 'Sector', 'Industry', 'P/E', 'Price', '%Change', 'Volume']]

def finviz_loosers(): 
    foverview = Overview()

    # Set filter for stocks with positive daily change
    #filters_dict = {'Change': 'Any', 'Current Volume': 'Over 1M'}
    #filters_dict = {'Change': 'Down 10%', 'Current Volume': 'Over 1M'}
    filters_dict = {'Change': 'Down 10%'}


    # Fetch the data
    foverview.set_filter(filters_dict=filters_dict)

    # Retrieve the screener data, ordering by Change
    df = foverview.screener_view(order='Change')
    df['%Change'] = df['Change']*100 

    # Sort the DataFrame by 'Change' in descending order
    #df['Change'] = df['Change'].str.rstrip('%').astype(float)  # Convert percentage strings to float
    df = df.sort_values(by='Change', ascending=True)

    # Display the results
    return df[['Ticker', 'Company', 'Sector', 'Industry', 'P/E', 'Price', '%Change', 'Volume']]

def parse_friendly_number(value_str):
    """
    Parses a string that might contain 'B' (billion), 'M' (million), or 'K' (thousand)
    suffixes and converts it into a raw float.
    Handles 'N/A' or non-parseable inputs by returning None.
    """
    if not isinstance(value_str, str):
        # If it's already a number or an unexpected type, return it directly
        return value_str

    value_str = value_str.strip().upper()

    if value_str == 'N/A' or not value_str:
        return None

    try:
        if value_str.endswith('B'):
            return float(value_str[:-1]) * 1_000_000_000
        elif value_str.endswith('M'):
            return float(value_str[:-1]) * 1_000_000
        elif value_str.endswith('K'):
            return float(value_str[:-1]) * 1_000
        elif value_str.endswith('%'): # For other metrics that might have %
            return float(value_str[:-1]) / 100
        else:
            return float(value_str)
    except ValueError:
        return None

def format_large_number(numeric_value, currency_symbol='$', decimal_places=2):
    """
    Formats a numeric value into a friendly string (e.g., "$53.47B", "$1.23M", "$45.67K").
    Handles None or non-numeric inputs by returning a default 'N/A'.

    Args:
        numeric_value: The number to format (e.g., 53470000000).
        currency_symbol (str): The currency symbol to prepend (default is '$').
        decimal_places (int): The number of decimal places to format to (default is 2).

    Returns:
        str: The formatted string.
    """
    if numeric_value is None or not isinstance(numeric_value, (int, float)):
        return 'N/A'

    if numeric_value == 0:
        return f"{currency_symbol}0"

    abs_value = abs(numeric_value)
    sign = '-' if numeric_value < 0 else ''

    if abs_value >= 1_000_000_000:
        return f"{sign}{currency_symbol}{abs_value / 1_000_000_000:.{decimal_places}f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}{currency_symbol}{abs_value / 1_000_000:.{decimal_places}f}M"
    elif abs_value >= 1_000:
        return f"{sign}{currency_symbol}{abs_value / 1_000:.{decimal_places}f}K"
    else:
        return f"{sign}{currency_symbol}{abs_value:.{decimal_places}f}"


def format_dataframe_market_cap(df):
    """
    Formats the 'Market Cap' column in a DataFrame to be more human-readable.
    It first attempts to parse existing friendly number strings into raw floats,
    then formats them consistently into '$X.XXB', '$X.XXM', or '$X.XXK' format.

    Args:
        df (pd.DataFrame): The input DataFrame. It's expected to have a 'Market Cap' column.

    Returns:
        pd.DataFrame: The DataFrame with the 'Market Cap' column formatted.
    """
    if 'Market Cap' not in df.columns:
        print("Warning: 'Market Cap' column not found in DataFrame.")
        return df

    # Apply parsing first, then formatting
    # Using .apply() with a lambda to process each value in the column
    df['Market Cap'] = df['Market Cap'].apply(
        lambda x: format_large_number(parse_friendly_number(x))
    )
    return df

def new_52_week_high(): 
    # Initialize the screener
    foverview = Overview()

    # Set filter for stocks at 52-week high
    filters_dict = {'52-Week High/Low': 'New High'}

    # Fetch the data
    foverview.set_filter(filters_dict=filters_dict)
    df_all = foverview.screener_view()
    df_some = df_all[(df_all['Volume'] > 1000000) & (~df_all['Company'].fillna('').str.endswith('ETF')) & (df_all['Country'] == 'USA')].reset_index()
    df = format_dataframe_market_cap(df_some.copy())
    tickers = df['Ticker'].to_list()  # Replace with a comprehensive list
    highs_within_10 = []
    highs_within_15 = []
    try: 
        # Fetch 52-week high data for each ticker
        print(f"Fetching 52-week high data for {len(tickers)} tickers...")
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info or 'regularMarketPrice' not in info or 'fiftyTwoWeekHigh' not in info:
                print(f"Skipping {ticker}: Missing essential info from yfinance.")
                continue

            if info['regularMarketPrice'] >= info['fiftyTwoWeekHigh'] * 0.90:  # Within 10% of 52-week high
                highs_within_10.append(ticker)
            elif info['regularMarketPrice'] >= info['fiftyTwoWeekHigh'] * 0.85:  # Within 15% of 52-week high
                highs_within_15.append(ticker)
    except Exception as e:
        print(f"Error fetching 52-week high data for {ticker}: {e}")
    for high in highs_within_10:
        df.loc[df['Ticker'] == high, 'Status'] = 'Within 10% of 52-Week High'
    for high in highs_within_15:
        df.loc[df['Ticker'] == high, 'Status'] = 'Within 15% of 52-Week High'
    df['Status'] = df['Status'].fillna('OverBought')  # Default status for stocks not within 10% or 15%
    return df.drop(columns='index')
#print(new_52_week_high())  # Example usage, replace with your desired ticker

def new_52_week_low(): 
    # Initialize the screener
    foverview = Overview()

    # Set filter for stocks at 52-week high
    filters_dict = {'52-Week High/Low': 'New Low'}

    # Fetch the data
    foverview.set_filter(filters_dict=filters_dict)
    df_all = foverview.screener_view()
    df_some = df_all[(df_all['Volume'] > 1000000) & (~df_all['Company'].fillna('').str.endswith('ETF')) & (df_all['Country'] == 'USA')].reset_index()
    df = format_dataframe_market_cap(df_some.copy())
    # Print the results
    return df.drop(columns='index')

def color_value_column(col):
    if col.name == 'Value':
        return ['color: red' if idx in [8,10,14,15] else '' for idx in col.index]
    else:
        # Return empty strings for other columns to avoid styling them
        return ['' for _ in col.index]
    

def get_finviz_fundamentals(ticker):
    """
    Fetch fundamental data for a given ticker from Finviz.
    """
    stock = finvizfinance(ticker)
    fundamentals = stock.ticker_fundament()

    # Get fundamental data for TSLA
    try:

    # Define the specific fundamentals you want to display
        desired_metrics = [
            'Company',
            'Sector',
            'Industry',
            'Insider Own',
            'Price',
            'Change',
            'Volume',
            'Shs Outstand',
            'Shs Float',
            'Inst Own',
            'Short Interest',
            'Market Cap', 
            'P/E', 
            'EPS (ttm)',
            'Avg Volume', 
            'Rel Volume',
            'Target Price',
            'Profit Margin',
            'ROE', 
            'Debt/Eq', 
            '52W High', 
            '52W Low'
        ]

        # Filter the fundamentals dictionary to include only desired metrics
        filtered_fundamentals = {key: fundamentals.get(key, 'N/A') for key in desired_metrics}

        # Create a DataFrame with one row
        df = pd.DataFrame([filtered_fundamentals])

        # Transpose the DataFrame for vertical display (metrics as rows, values as a column)
        df_transposed = df.T.reset_index()
        df_transposed.columns = ['Metric', 'Value']

        
        current_price_str = filtered_fundamentals.get('Price', 'N/A')
        current_price = float(current_price_str) if current_price_str != 'N/A' else None



        #df_transposed.loc[df_transposed['Metric'] == '52W High', 'Value'] = actual_52W_high
        #df_transposed.loc[df_transposed['Metric'] == '52W Low', 'Value'] = actual_52W_low

        # Display the table
        style.use('ggplot')  # Optional: Set a style for better aesthetics
        styled_df = df_transposed.style.apply(color_value_column)
        output_image_path = os.path.join('static', 'styled_df.png')
        print(tabulate(df_transposed, headers='keys', tablefmt='psql', showindex=False))
        dfi.export(styled_df, output_image_path, max_rows=-1)
        return 'styled_df.png'

    except Exception as e:
        return f'An error occurred: {e} - {ticker}'
    
def news(ticker):
    """
    Fetch news headlines for a given ticker.
    """ 
    try: 
        stock = finvizfinance(ticker)
        news = stock.ticker_news()
        news['Date'] = pd.to_datetime(news['Date'], errors='coerce')
        news.sort_values(by='Date', ascending=False, inplace=True)
        if 'Link' in news.columns:
            # Create HTML <a> tags for the URLs
            # Using a lambda function to apply the formatting to each link
            news['URL'] = news['Link'].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>')
            # Drop the original 'url' column if you don't want it displayed
            news = news.drop(columns=['Link'], errors='ignore')  # Use errors='ignore' to avoid KeyError if 'Link' doesn't exist
        else:
            news['URL'] = 'N/A' # Add a 'Link' column even if no URLs

        # get news from the last 5 days 
        today = datetime.now().strftime('%Y-%m-%d')
        five_days_ago = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        news = news[(news['Date'].dt.strftime('%Y-%m-%d') >= five_days_ago)]
        if news.empty:
            return f"No news found for {ticker} in the last 5 days."
        return news[['Date', 'Title', 'URL', 'Source']]
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return f"An error occurred while fetching news for {ticker}."

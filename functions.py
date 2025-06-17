import pandas as pd
import yfinance as yf
from finvizfinance.screener.overview import Overview
from datetime import datetime, timedelta


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

def new_52_week_high(): 
    # Initialize the screener
    foverview = Overview()

    # Set filter for stocks at 52-week high
    filters_dict = {'52-Week High/Low': 'New High'}

    # Fetch the data
    foverview.set_filter(filters_dict=filters_dict)
    df_all = foverview.screener_view()
    df = df_all[(df_all['Volume'] > 1000000) & (~df_all['Company'].fillna('').str.endswith('ETF')) & (df_all['Country'] == 'USA')].reset_index()

    # Print the results
    return df.drop(columns='index')

def new_52_week_low(): 
    # Initialize the screener
    foverview = Overview()

    # Set filter for stocks at 52-week high
    filters_dict = {'52-Week High/Low': 'New Low'}

    # Fetch the data
    foverview.set_filter(filters_dict=filters_dict)
    df_all = foverview.screener_view()
    df = df_all[(df_all['Volume'] > 1000000) & (~df_all['Company'].fillna('').str.endswith('ETF')) & (df_all['Country'] == 'USA')].reset_index()

    # Print the results
    return df.drop(columns='index')
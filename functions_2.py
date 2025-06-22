import matplotlib
matplotlib.use('Agg') # This line MUST come before importing pyplot or mplfinance
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.dates import DateFormatter, DayLocator
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import mplfinance as mpf
import os
import traceback

def calculate_heikin_ashi(df):
    """
    Calculate Heikin-Ashi OHLC values from standard OHLC data.
    Returns a DataFrame with Heikin-Ashi columns.
    """
    try:
        ha_df = pd.DataFrame(index=df.index)
        ha_df['Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
        ha_df['Open'] = df['Open'].iloc[0]
        for i in range(1, len(df)):
            ha_df['Open'].iloc[i] = (ha_df['Open'].iloc[i-1] + ha_df['Close'].iloc[i-1]) / 2
        ha_df['High'] = df[['High', 'Open', 'Close']].max(axis=1)
        ha_df['Low'] = df[['Low', 'Open', 'Close']].min(axis=1)
        if 'Volume' in df.columns:
            ha_df['Volume'] = df['Volume']
        print(f"Calculated Heikin-Ashi for {len(ha_df)} rows")
        return ha_df
    except Exception as e:
        print(f"Error in calculate_heikin_ashi: {e}\n{traceback.format_exc()}")
        raise

def indices_chart():
    """
    Fetches the latest data for major stock indices and returns a DataFrame.
    """
    indices = ['^DJI', '^GSPC', '^IXIC', '^RUT']
    chart_paths = {}
    for index in indices:
        print(f"Fetching data for {index}") 
        raw_data = yf.download(index, period='1d', interval='1m')
        times_total = raw_data.index.map(lambda x: x.strftime("%H:%M:%S")).tolist()
        times_EDT = [pd.to_datetime(time) - timedelta(hours=4) for time in times_total]  # Adjusting to EDT
        #times = [time.strftime("%H:%M:%S") for time in times_EDT]
        df = pd.DataFrame(raw_data.values, columns=['Close', 'High', 'Low', 'Open', 'Volume'])
        df.insert(0, 'Time', times_EDT)
        df.set_index('Time', inplace=True)
        print(df)
        save_path = os.path.join('static', f'{index}_heikin_ashi.png')
        print(f"Attempting to plot chart for {index} at {save_path}")

        # Create a custom style to adjust font sizes
 
        mpf.plot(
            df,
            type='candle',
            style='yahoo',
            savefig=save_path,
            title=f'{index} for {datetime.now().strftime("%Y-%m-%d")}',
            figsize=(20, 12),
            tight_layout=True,
            ylabel='Price',
            xlabel='Time (EDT)',
            xrotation=45
            )
        print(f"Chart saved for {index} at {save_path}")
        chart_paths[index] = save_path
    return chart_paths


def plot_chart(ticker):
    """
    Generate data for plotting trading volume and close price of a stock over a specified date range.
    Returns JSON-compatible data for Chart.js.
    """
    try:
        raw_data = yf.download(ticker, period='1d', interval='1m')
        times_total = raw_data.index.map(lambda x: x.strftime("%H:%M:%S")).tolist()
        times_EDT = [pd.to_datetime(time) - timedelta(hours=4) for time in times_total]  # Adjusting to EDT
        #times = [time.strftime("%H:%M:%S") for time in times_EDT]
        df = pd.DataFrame(raw_data.values, columns=['Close', 'High', 'Low', 'Open', 'Volume'])
        df.insert(0, 'Time', times_EDT)
        df.set_index('Time', inplace=True)

        # --- Potential problem area: Data types and NaNs ---
        # Ensure 'Close' and 'Volume' are numeric and handle missing values
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        df['Volume'].iloc[0] = 0  
        df['Volume'].iloc[-3] = 0
        df['Volume'].iloc[-2] = 0
        df['Volume'].iloc[-1] = 0  
        # Drop rows where 'Close' or 'Volume' became NaN after conversion
        df = df.dropna(subset=['Close', 'Volume'])

        ha_df = calculate_heikin_ashi(df)
        print(ha_df)
        
        # Plot the volume and close price with compressed layout
        fig, (ax_price, ax_volume) = plt.subplots(nrows=2, ncols=1, sharex=True,
                                                  gridspec_kw={'height_ratios': [3, 1]}, # Price panel 3x taller than volume
                                                  figsize=(12, 8), # Overall figure size (width, height in inches)
                                                  facecolor='#1e1e3f') # Set figure background here
        
        save_path = os.path.join('static', f'{ticker}_heikin_ashi.png')
        mpf.plot(
            ha_df,
            type='candle',
            style='yahoo',
            volume=True,
            panel_ratios=(3, 1),  # Price panel 3x taller than volume
            savefig=save_path,
            title=f'{ticker} for {datetime.now().strftime("%Y-%m-%d")}',
            tight_layout=True,
            ylabel='Price',
            ylabel_lower='Volume (x10^5)',
            xlabel='Time (EDT)',
            xrotation=45,
            warn_too_much_data=1000,  # Prevent warnings about too much data
            )
        print(f"Combined Heikin-Ashi and Volume chart saved for {ticker} at {save_path}.")
        return save_path
    except Exception as e:
        print(f"Error generating combined chart for {ticker}: {str(e)}")
        print(traceback.format_exc())
        return None
    

def clean_static_folder():
    """
    Deletes all files in the 'static' folder except for 'styles.css'.
    """
    static_path = os.path.join(os.path.dirname(__file__), 'static')

    # Ensure the static directory exists before trying to list its contents
    if not os.path.exists(static_path):
        print(f"Static folder not found at: {static_path}. Nothing to clean.")
        return

    for filename in os.listdir(static_path):
        file_path = os.path.join(static_path, filename)
        
        try:
            # Check if it's a file and not 'styles.css'
            if os.path.isfile(file_path) and filename != 'styles.css':
                os.unlink(file_path)
                print(f"Deleted: {filename}") # Optional: print which file is deleted
            elif filename == 'styles.css':
                print(f"Skipping styles.css") # Optional: confirm it's skipped
            # Optional: Add an else if you want to handle subdirectories
            # elif os.path.isdir(file_path):
            #     print(f"Skipping directory: {filename}")
        except Exception as e:
            print(f"Error deleting {file_path}: {str(e)}")

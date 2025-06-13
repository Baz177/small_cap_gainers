from datetime import datetime, timedelta
import yfinance as yf 
import pandas as pd 
from functions import get_micro_cap_stocks, get_small_cap_stocks, gainers
from flask import Flask, render_template, request
from itertools import islice
import os
from waitress import serve 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_gainers', methods=['GET'])
def get_gainers():
    # Load data (assuming files exist)
    micro_cap_stocks = pd.read_csv('micro_cap_stocks.csv')
    small_cap_stocks = pd.read_csv('small_cap_stocks.csv')

    # Combine and process data
    stocks_df = pd.concat([small_cap_stocks, micro_cap_stocks], ignore_index=True)
    stocks_df = stocks_df.drop_duplicates(subset='Ticker', keep='first')
    stocks_df = stocks_df.dropna(subset=['Ticker', 'Company'])

    tickers = stocks_df['Ticker'].to_list()
    company_names = stocks_df['Company'].to_list()

    assert len(tickers) == len(company_names), "Ticker and Company lists have different lengths"

    # Zip and slice
    company_tickers = zip(tickers, company_names)
    sliced_company_tickers = tuple(islice(company_tickers, 1, 400))

    # Process gainers
    gainers_df = gainers(company_tickers)
    df_sorted = gainers_df.sort_values(by='%Change', ascending=False)
    df = df_sorted[df_sorted['%Change'] > 10].reset_index(drop=True)
    df[df.select_dtypes(include='float64').columns] = df.select_dtypes(include='float64').apply(lambda x: round(x, 2))

    # Save table to static folder
    table_html = df.to_html(classes='table table-striped table-bordered', index=False)
    with open('static/gainers_table.html', 'w') as f:
        f.write(table_html)

    date = datetime.now().strftime('%B %d, %Y')
    return render_template('gainers.html', table=table_html, date=date)
    
if __name__ == '__main__':
    print("Starting Waitress server...")
    serve(app, host='0.0.0.0', port=5000)
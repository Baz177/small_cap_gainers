from datetime import datetime, timedelta
import yfinance as yf 
import pandas as pd 
from functions import get_micro_cap_stocks, get_small_cap_stocks, gainers, new_52_week_high, finviz_gainers, finviz_loosers
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
    # Load data 
    #micro_cap_stocks = pd.read_csv('micro_cap_stocks.csv')
    #small_cap_stocks = pd.read_csv('small_cap_stocks.csv')

    # Combine and process data
    #stocks_df = pd.concat([small_cap_stocks, micro_cap_stocks], ignore_index=True)
    #stocks_df = stocks_df.drop_duplicates(subset='Ticker', keep='first')
    #stocks_df = stocks_df.dropna(subset=['Ticker', 'Company'])

    #tickers = stocks_df['Ticker'].to_list()
    #company_names = stocks_df['Company'].to_list()

    #assert len(tickers) == len(company_names), "Ticker and Company lists have different lengths"

    # Zip and slice
    #company_tickers = zip(tickers, company_names)
    #sliced_company_tickers = tuple(islice(company_tickers, 1, 400))

    # Process gainers
    gainers_df = finviz_gainers()

    # Process loosers
    looser_df = finviz_loosers()

    # 52 week high table 
    table_52 = new_52_week_high()

    # Save table to static folder
    table_html_1 = gainers_df.to_html(classes='table table-striped table-bordered', index=False)
    with open('static/gainers_table.html', 'w') as f:
        f.write(table_html_1)

    table_html_2 = looser_df.to_html(classes='table table-striped table-bordered', index=False)
    with open('static/loosers_table.html', 'w') as f:
        f.write(table_html_2)
    

    table_html_3 = table_52.to_html(classes='table table-striped table-bordered', index=False)
    with open('static/52_week_table.html', 'w') as f:
        f.write(table_html_3)
    

    date = datetime.now().strftime('%B %d, %Y')
    return render_template('gainers.html', table_1=table_html_1, table_2 = table_html_2, table_3 = table_html_3, date=date)
    
if __name__ == '__main__':
    print("Starting Waitress server...")
    serve(app, host='0.0.0.0', port=5000)
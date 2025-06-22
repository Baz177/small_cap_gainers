from datetime import datetime, timedelta
import yfinance as yf 
import pandas as pd 
from functions import get_micro_cap_stocks, get_small_cap_stocks, gainers, new_52_week_high, finviz_gainers, finviz_loosers, new_52_week_low, get_finviz_fundamentals, news
from functions_2 import indices_chart, clean_static_folder, plot_chart
from flask import Flask, render_template, request
from finvizfinance.quote import finvizfinance
from itertools import islice
import os
from waitress import serve 

app = Flask(__name__)

@app.route('/')
@app.route('/')
def index():
    # Call the function to generate charts and get their paths
    image_paths = indices_chart() 
    print(f"Image paths generated: {image_paths}")
    # Pass the dictionary of image paths to the HTML template
    return render_template('index.html', image_paths=image_paths)

@app.route('/scanner')
def scanner():
    """
    Render the scanner page.
    """
    try:
        return render_template('scanner.html')
    except Exception as e:
        print(f"Error in scanner route: {e}")
        return render_template('error.html', error_message=str(e))

@app.route('/get_gainers', methods=['GET'])
def get_gainers():
    """
    Fetch and display selected tables based on user input (gainers, losers, 52-week high/low stocks).
    """
    try:
        options = request.args.getlist('options')
        if not options:
            options = ['gainers', 'losers', '52weekhigh', '52weeklow']
        table_html_1 = table_html_2 = table_html_3 = table_html_4 = None
        if 'gainers' in options:
            gainers_df = finviz_gainers()
            table_html_1 = gainers_df.to_html(classes='table table-striped table-bordered', index=False)
            with open('static/gainers_table.html', 'w') as f:
                f.write(table_html_1)
        if 'losers' in options:
            looser_df = finviz_loosers()
            table_html_2 = looser_df.to_html(classes='table table-striped table-bordered', index=False)
            with open('static/loosers_table.html', 'w') as f:
                f.write(table_html_2)
        if '52weekhigh' in options:
            table_52_high = new_52_week_high()
            table_html_3 = table_52_high.to_html(classes='table table-striped table-bordered', index=False)
            with open('static/52_week_table.html', 'w') as f:
                f.write(table_html_3)
        if '52weeklow' in options:
            table_52_low = new_52_week_low()
            table_html_4 = table_52_low.to_html(classes='table table-striped table-bordered', index=False)
            with open('static/52_week_table_low.html', 'w') as f:
                f.write(table_html_4)
        date = datetime.now().strftime('%B %d, %Y')
        return render_template('gainers.html', 
                              table_1=table_html_1, 
                              table_2=table_html_2, 
                              table_3=table_html_3, 
                              table_4=table_html_4, 
                              date=date,
                              show_gainers='gainers' in options,
                              show_losers='losers' in options,
                              show_52weekhigh='52weekhigh' in options,
                              show_52weeklow='52weeklow' in options)
    except Exception as e:
        print(f"Error in get_gainers: {e}")
        return render_template('error.html', error_message=str(e))

@app.route('/get_fundamentals', methods=['POST'])
def get_fundamentals():
    ticker = request.form.get('ticker', '').upper()
    if ticker:
        
        table_path = get_finviz_fundamentals(ticker)

        chart_file_path = plot_chart(ticker) # Call your chart generation function

        df_news = news(ticker)
        news_table_html = df_news.to_html(
            classes='table table-striped table-bordered',
            index=False,
            escape=False # <--- THIS IS THE KEY ADDITION
        ) if not df_news.empty else None

        # Extract just the filename for URL_for
        chart_filename = os.path.basename(chart_file_path) if chart_file_path else None

        # Pass today's date
        current_date = datetime.now().strftime("%Y-%m-%d")

        return render_template(
            'fundamentals.html',
            ticker=ticker,
            table=table_path,
            date=current_date, # Pass the date
            chart_filename=chart_filename,
            news_table=news_table_html
        )
    else:
        return "Please provide a ticker symbol.", 400

if __name__ == '__main__':
    print("Starting Waitress server...")
    clean_static_folder()  # Clean static folder before starting server
    serve(app, host='0.0.0.0', port=5000)
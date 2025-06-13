# Stock Gainers Application

This is a Flask-based web application that analyzes micro and small-cap stock data to identify top gainers with a percentage change greater than 10%. The application fetches data from CSV files, processes it, and displays the results in a styled table. It is deployed using Waitress, a production-ready WSGI server.

## Features
- Analyzes stock data from `micro_cap_stocks.csv` and `small_cap_stocks.csv`.
- Filters stocks with a percentage change greater than 10%.
- Displays results in a responsive table with rounded numerical values.
- Includes a loading animation during data processing.
- Saves the table as an HTML file in the `static` folder.
- Left-aligned index page with a "Get Gainers" button.
- Dynamic heading on the gainers page showing "Small cap stock gainers for {today's date} greater than 10%".

## Requirements
- Python 3.7 or higher
- Required Python packages:
  - `flask`
  - `pandas`
  - `waitress`

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd stock-gainers-app
```

### Install dependancies
pip install -r requirements.txt


## Usage
1. Open a web browser and navigate to http://127.0.0.1:5000/.
2. On the index page, click the "Get Gainers" button.
3. A loading animation will appear while the data is processed (simulated delay of 2 seconds).
4. Once processed, the gainers table will display with the heading "Small cap stock gainers for June 13, 2025 greater than 10%".
5. Click "Back to Home" to return to the index page

## File Structure 

<pre>
stock-gainers-app/
├── static/
│   └── gainers_table.html    # Saved table HTML
│   └── style.css            # Custom CSS for styling
├── templates/
│   └── index.html           # Main page with "Get Gainers" button
│   └── gainers.html         # Page displaying the gainers table
├── app.py                   # Flask application logic
├── wsgi.py                  # Waitress server configuration
├── micro_cap_stocks.csv     # Micro-cap stock data
├── small_cap_stocks.csv     # Small-cap stock data
├── README.md                # This documentation
└── requirements.txt         # Python dependencies (optional)
</pre>

## Contact
For questions or support, contact bazdiozt@gmail.com or open an issue on the repository.

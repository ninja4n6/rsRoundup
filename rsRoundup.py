import requests
import yfinance as yf
from datetime import datetime, timedelta
import re

print("               ____                        __           ")
print("    __________/ __ \\____  __  ______  ____/ /_  ______  ")
print("   / ___/ ___/ /_/ / __ \\/ / / / __ \\/ __  / / / / __ \\ ")
print("  / /  (__  ) _, _/ /_/ / /_/ / / / / /_/ / /_/ / /_/ / ")
print(" /_/  /____/_/ |_|\\____/\\__,_/_/ /_/\\__,_/\\__,_/ .___/  ")
print("                                               /_/      ")

print("rsRoundup script v1.0 created by @Braydio aka @bchaffee23")
print("Contributions by @echo and @ckzz on Xtrades")
print("https://github.com/bchaffee23/rsRoundup\n\n")

# --- Configuration ---
url = "https://efts.sec.gov/LATEST/search-index"
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
params = {
    "q": "\"reverse split\" OR \"fractional shares\"",  
    "dateRange": "custom",
    "startdt": start_date,
    "enddt": end_date,
    "category": "full",
    "start": 0,
    "count": 100 
}

# --- Functions ---
def get_ticker_symbols(display_names):
    tickers = []
    for name in display_names:
        match = re.search(r"\(([^)]+)\)", name)  # Find text within parentheses
        if match:
            tickers.extend(match.group(1).replace(",", "").split()) # Split if multiple tickers
    return tickers

def write_results_to_file(results, filename='output.txt'):
    unique_file_numbers = set()  # Track unique file numbers

    with open(filename, 'w') as f:
        f.write(f"Total Unique Results: {len(results)}\n\n")  # Count unique results
        for result in results:
            # Check if file number is already processed
            if result['file_number'] not in unique_file_numbers: 
                unique_file_numbers.add(result['file_number'])

                for key, value in result.items():
                    f.write(f"{key.capitalize()}: {value}\n")
                if result['tickers']:
                    tradingview_url = f"https://www.tradingview.com/chart/?symbol={result['tickers'][0]}"
                    f.write(f"TradingView URL: {tradingview_url}\n\n")
                else:
                    f.write("TradingView URL: N/A\n\n")


# --- Main Script ---
try:
    response = requests.get(url, params=params, headers={"User-Agent": "MyApp/1.0 (my.email@example.com)"})
    response.raise_for_status()
    data = response.json()

    results = []
    if 'hits' in data and 'hits' in data['hits']:
        for result in data['hits']['hits']:
            form_type = result['_source'].get('form', 'N/A')
            if form_type in ['8-K', 'S-1', 'S-3', 'S-4']: 
                filing_info = {
                    "file_number": result['_source'].get('file_num', ['N/A'])[0],
                    "form_type": form_type,
                    "primary_doc_description": result['_source'].get('file_description', 'N/A'),
                    "file_date": result['_source'].get('file_date', 'N/A'),
                    "period_ending": result['_source'].get('period_ending', 'N/A'),
                    "display_names": result['_source'].get('display_names', []),
                    "tickers": get_ticker_symbols(result['_source'].get('display_names', []))
                }
                results.append(filing_info)

    # Remove duplicates based on file number
    results = list({r['file_number']: r for r in results}.values())  # Convert to list to filter
    filtered_results = filter(lambda x: 'file_date' in x, results)

    sorted_results = sorted(
        filtered_results,  # Pass filtered results to sorted
        key=lambda x: datetime.strptime(x['file_date'], '%Y-%m-%d') if 'file_date' in x else datetime.min,  
        reverse=True
    )
    write_results_to_file(sorted_results)

    print(f"\nrsRoundup located {len(sorted_results)} filings...\n")
    print("Results are saved in 'output.txt'\n")

except requests.exceptions.RequestException as e:
    with open('output.txt', 'w') as f:
        f.write(f"Request failed: {e}\n")
    print(f"Request failed: {e}")

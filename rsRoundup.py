import requests
from datetime import datetime, timedelta

# Define the endpoint and parameters
url = "https://efts.sec.gov/LATEST/search-index"
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
params = {
    "q": "\"reverse split\" AND \"no fractional shares\" AND \"round\" OR \"rounded\"",
    "dateRange": "custom",
    "startdt": start_date,
    "enddt": end_date,
    "category": "full",
    "start": 0,
    "count": 10
}

# Make the request
try:
    response = requests.get(url, params=params, headers={"User-Agent": "MyApp/1.0 (my.email@example.com)"})
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    data = response.json()

    # Collect the results
    results = []
    if 'hits' in data and 'hits' in data['hits']:
        for result in data['hits']['hits']:
            form_type = result['_source'].get('form', 'N/A')
            if form_type == '8-K':
                file_number = result['_source'].get('file_num', ['N/A'])[0]
                primary_doc_description = result['_source'].get('file_description', 'N/A')
                file_date = result['_source'].get('file_date', 'N/A')
                period_ending = result['_source'].get('period_ending', 'N/A')
                display_names = ', '.join(result['_source'].get('display_names', ['N/A']))
                results.append({
                    "file_number": file_number,
                    "form_type": form_type,
                    "primary_doc_description": primary_doc_description,
                    "file_date": file_date,
                    "period_ending": period_ending,
                    "display_names": display_names
                })

    # Sort the results by file_date in descending order
    sorted_results = sorted(results, key=lambda x: datetime.strptime(x['file_date'], '%Y-%m-%d'), reverse=True)

    # Write the sorted results to output.txt
    with open('output.txt', 'w') as f:
        f.write(f"Total Results: {len(sorted_results)}\n\n")
        for result in sorted_results:
            f.write(f"File Number: {result['file_number']}\n")
            f.write(f"Form Type: {result['form_type']}\n")
            f.write(f"Description: {result['primary_doc_description']}\n")
            f.write(f"File Date: {result['file_date']}\n")
            f.write(f"Period Ending: {result['period_ending']}\n")
            f.write(f"Company Name(s): {result['display_names']}\n\n")
except requests.exceptions.RequestException as e:
    with open('output.txt', 'w') as f:
        f.write(f"Request failed: {e}\n")

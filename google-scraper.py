import requests
import csv
import re
from tqdm import tqdm
import config # it has the 2 api key 
# Function to search using Google Custom Search and save results to a CSV file
def search_and_save_to_csv(api_key, cse_id, query, csv_file_path, max_results=100):
    url = "https://www.googleapis.com/customsearch/v1"
    results_fetched = 0  # Keep track of how many results have been fetched

  # Update the regex patterns
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    url_pattern = re.compile(r'\b(?:https?://)?[^\s]+[.][^\s]+\b')

    try:
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Updated headers to include email and other links
            headers = ['Title', 'Link', 'Snippet', 'Email', 'Other Links']
            writer.writerow(headers)

            # Set up the progress bar
            pbar = tqdm(total=max_results, unit="result")

            while results_fetched < max_results:
                params = {
                    'key': api_key,
                    'cx': cse_id,
                    'q': query,
                    'start': results_fetched + 1  # Start at the next result
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                search_results = response.json().get('items', [])
                
                if not search_results:
                    break  # Exit the loop if no more results are returned
                
                for result in search_results:
                    title = result.get('title')
                    link = result.get('link')
                    snippet = result.get('snippet')
                    
                    # Extract emails and URLs from the snippet
                    emails = ', '.join(set(email_pattern.findall(snippet)))
                    urls = ', '.join(set(url for url in url_pattern.findall(snippet) if not any(email in url for email in emails)))

                   # Write the row with extracted email and URLs
                    writer.writerow([title, link, snippet, emails, urls])

                    # Update the progress bar for each result processed
                    pbar.update(1)
                
                results_fetched += len(search_results)  # Update the number of fetched results
                
                # Check if there are more results pages
                if 'queries' in response.json() and 'nextPage' in response.json()['queries']:
                    continue  # If there's a next page, continue fetching
                else:
                    break  # If there's no next page, exit the loop

            # Close the progress bar
            pbar.close()

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except csv.Error as e:
        print(f"CSV error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
api_key = config.api_key #api_key = 'You can insert your api key here'
cse_id = config.cse_id #cse_id= 'You can insert your google cse id  here'
query = 'founder intext:gmail.com site:instagram.com -site:"https://www.instagram.com/p/" inurl:/reels'
csv_file_path = 'search_results.csv'

search_and_save_to_csv(api_key, cse_id, query, csv_file_path, max_results=100)

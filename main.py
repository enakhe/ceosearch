import requests
import spacy
import re

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract emails from a given text
def extract_emails(text):
    # Regular expression for extracting email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)


# Function to extract entries from file
def extract_entries_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split content by double newlines (assuming each entry is separated by double newlines)
    entries = content.split('\n')
    return entries


# Function to extract domain from email
def get_domain_from_email(email):
    return email.split('@')[1]


# Function to search for CEO using Google Custom Search API
def search_ceo_google(domain, api_key, search_engine_id):
    search_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q=CEO+of+{domain}"
    response = requests.get(search_url)
    if response.status_code == 200:
        search_results = response.json()
        if 'items' in search_results:
            for item in search_results['items']:
                snippet = item.get('snippet', '')
                # Process the snippet with spaCy to find named entities
                doc = nlp(snippet)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        return ent.text
    return "No information found"


# Function to format output for each entry
def format_output(ceo_name, entry):
    return f"{ceo_name}\n{entry}\n\n"


# Function to read API keys and search engine IDs from file
def read_api_keys(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Split the lines into pairs
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines), 2)]
    return pairs


# Example usage
file_path = 'entry.txt'
output_file = 'output.txt'
api_keys_file = 'api_keys.txt'
counter = 0

# Extract entries from file
entries = extract_entries_from_file(file_path)

# Read API keys and search engine IDs
api_pairs = read_api_keys(api_keys_file)

# Initialize search count and API pair index
search_count = 0
api_pair_index = 0

# Open output file for writing
with open(output_file, 'w') as file_out:
    # Iterate over each entry
    for entry in entries:
        counter += 1
        emails = extract_emails(entry)
        if emails:
            domain = get_domain_from_email(emails[0])

            # Check if we need to switch to the next API pair
            if search_count >= 100:
                search_count = 0
                api_pair_index += 1
                if api_pair_index >= len(api_pairs):
                    print("Exhausted all API keys and search engine IDs.")
                    break

            # Get the current API key and search engine ID
            api_key, search_engine_id = api_pairs[api_pair_index]

            # Search for the CEO using the current API key and search engine ID
            ceo_name = search_ceo_google(domain, api_key, search_engine_id)
            formatted_entry = format_output(ceo_name, entry)
            file_out.write(formatted_entry)

            # Increment the search count
            search_count += 1

print(counter)
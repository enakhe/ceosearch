import requests
import spacy
import re

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract emails from a given text
def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

# Function to extract entries from file
def extract_entries_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
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

# Function to clean entry, ensuring only the first and last name before the email
def clean_entry(entry):
    words = entry.split()
    for i, word in enumerate(words):
        if '@' in word:
            email_index = i
            break
    # Extract the first name, last name, and email
    first_name = words[0]
    last_name = words[email_index - 1]
    email = words[email_index]
    cleaned_entry = f"{first_name} {last_name} {email}"
    return cleaned_entry

# Function to clean the CEO name, removing any apostrophes and everything after
def clean_ceo_name(ceo_name):
    # Remove apostrophes and everything after
    ceo_name = ceo_name.split("'")[0].strip()
    # Split the name into words and take only the first and last names
    name_parts = ceo_name.split()
    if len(name_parts) > 2:
        ceo_name = f"{name_parts[0]} {name_parts[-1]}"
    return ceo_name

# Function to format output for each entry
def format_output(ceo_name, entry):
    ceo_name = clean_ceo_name(ceo_name)
    cleaned_entry = clean_entry(entry)
    domain = get_domain_from_email(extract_emails(entry)[0])
    return f"{ceo_name}\n{cleaned_entry}\n\n"

# Function to read API keys and search engine IDs from file
def read_api_keys(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines), 2)]
    return pairs

# Example usage
file_path = 'entry.txt'
output_file = 'output.txt'
api_keys_file = 'api_keys.txt'

# Extract entries from file
entries = extract_entries_from_file(file_path)

# Read API keys and search engine IDs
api_pairs = read_api_keys(api_keys_file)

# Initialize search count and API pair index
search_count = 0
api_pair_index = 0

# Open output file for writing
with open(output_file, 'w', encoding='utf-8') as file_out:
    # Iterate over each entry
    for entry in entries:
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

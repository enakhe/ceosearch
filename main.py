import requests
import spacy
import re

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Google Custom Search API credentials
api_key = 'AIzaSyCCA_9NsoTy82n8qk1--5fYAH8_zXHsIpM'
search_engine_id = '3088e01757ce14d6f'
counter = 0


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
def search_ceo_google(domain):
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


# Example usage
file_path = 'entry.txt'
output_file = 'output.txt'

# Extract entries from file
entries = extract_entries_from_file(file_path)

# Open output file for writing
with open(output_file, 'w') as file_out:
    # Iterate over each entry
    for entry in entries:
        emails = extract_emails(entry)
        if emails:
            domain = get_domain_from_email(emails[0])
            ceo_name = search_ceo_google(domain)
            formatted_entry = format_output(ceo_name, entry)
            file_out.write(formatted_entry)
            counter += 1


print(counter)
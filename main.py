import requests
import spacy
import re
from models import CEO  # Import the CEO model to interact with the database

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")


def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)


def extract_entries_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    entries = content.split('\n')
    return entries


def get_domain_from_email(email):
    return email.split('@')[1]


def search_ceo_google(domain, api_key, search_engine_id):
    search_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q=CEO+of+{domain}"
    response = requests.get(search_url)
    if response.status_code == 200:
        search_results = response.json()
        if 'items' in search_results:
            for item in search_results['items']:
                snippet = item.get('snippet', '')
                doc = nlp(snippet)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        return ent.text
    return "No information found"


def clean_entry(entry):
    words = entry.split()
    for i, word in enumerate(words):
        if '@' in word:
            email_index = i
            break
    first_name = words[0]
    last_name = words[email_index - 1]
    email = words[email_index]
    cleaned_entry = f"{first_name} {last_name} {email}"
    return cleaned_entry


def clean_ceo_name(ceo_name):
    ceo_name = ceo_name.split("'")[0].strip()
    name_parts = ceo_name.split()
    if len(name_parts) > 2:
        ceo_name = f"{name_parts[0]} {name_parts[-1]}"
    return ceo_name


def format_output(ceo_name, entry):
    ceo_name = clean_ceo_name(ceo_name)
    cleaned_entry = clean_entry(entry)
    domain = get_domain_from_email(extract_emails(entry)[0])
    return f"{ceo_name}\n{cleaned_entry}\n\n"


def read_api_keys(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines), 2)]
    return pairs


file_path = 'data/entry.txt'
output_file = 'data/output.txt'
api_keys_file = 'data/api_keys.txt'

entries = extract_entries_from_file(file_path)
api_pairs = read_api_keys(api_keys_file)

search_count = 0
api_pair_index = 0

with open(output_file, 'w', encoding='utf-8') as file_out:
    for entry in entries:
        emails = extract_emails(entry)
        if emails:
            email = emails[0]
            domain = get_domain_from_email(email)

            # Check if the email already exists in the database
            existing_ceo = CEO.get_ceo_by_email(email)
            if existing_ceo:
                # Format and write the existing CEO info to output file
                formatted_entry = format_output(existing_ceo['ceo'], entry)
            else:
                if search_count >= 100:
                    search_count = 0
                    api_pair_index += 1
                    if api_pair_index >= len(api_pairs):
                        print("Exhausted all API keys and search engine IDs.")
                        break

                api_key, search_engine_id = api_pairs[api_pair_index]
                ceo_name = search_ceo_google(domain, api_key, search_engine_id)

                # Save the CEO name and email to the database
                new_ceo = CEO(ceo_name, email)
                new_ceo.save_to_db()

                formatted_entry = format_output(ceo_name, entry)

            file_out.write(formatted_entry)
            search_count += 1

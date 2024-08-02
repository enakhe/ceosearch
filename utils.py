# main.py
from models import CEO

def add_entries_to_db(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    ceo_name = None
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) > 1 and '@' in parts[-1]:
                email = parts[-1]
                if ceo_name:
                    ceo = CEO(ceo_name, email)
                    ceo.save_to_db()
                ceo_name = parts[0] + " " + parts[1]
            else:
                ceo_name = line.strip()


if __name__ == "__main__":
    add_entries_to_db('data/searched_entry.txt')

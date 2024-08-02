from db_config import get_database

db = get_database()


class CEO:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save_to_db(self):
        ceo_collection = db['ceos']
        ceo_collection.insert_one({
            "ceo": self.name,
            "email": self.email
        })

    @staticmethod
    def get_ceo_by_email(email):
        ceo_collection = db['ceos']
        return ceo_collection.find_one({"email": email})
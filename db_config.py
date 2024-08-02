# ceosearch/db_config.py

from pymongo import MongoClient

def get_database():
    client = MongoClient("mongodb://localhost:27017")
    return client['ceo_search_db']

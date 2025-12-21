from pymongo import MongoClient
from bson.objectid import ObjectId
import json

class MongoDBFetcher:
    def __init__(self, connection_string, database_name, collection_name):
        try:
            # Connect to MongoDB Atlas
            self.client = MongoClient(connection_string)
            self.database = self.client[database_name]  # Database Name
            self.collection = self.database[collection_name]  # Collection Name
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None
    
    def fetch_data_by_asin(self, asin):
        try:
            # Query the collection to find documents matching the given ASIN
            query = {"asin": asin}
            product_data = self.collection.find_one(query)
            
            if product_data:
                return product_data
            else:
                print(f"No data found for ASIN: {asin}")
                return None
        except Exception as e:
            print(f"Error fetching data from MongoDB: {e}")
            return None


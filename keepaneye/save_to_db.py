from keepaneye.api_call import ApiCall
from keepaneye.read_creds import AppConfig
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class SaveToDB:
    def data_load(self,product_results):
        try:
            self.product_results = product_results
            self.__config = AppConfig()
            self.db_uri = f"mongodb+srv://{self.__config.DATABASE_USER}:{self.__config.DATABASE_PASSWORD}@cluster0.25acfan.mongodb.net/?appName=Cluster0"
            client = MongoClient(self.db_uri, server_api=ServerApi('1'))
            database = client["AWS_TRACKER"]
            collection = database["AWS_TRACKER_PYTHON"]
            document = {
               "asin": product_results.get('product_results', {}).get('asin', 'unknown'),
                "stock": product_results.get('product_results', {}).get('stock', 'Unknown'),
                "title": product_results.get('product_results', {}).get('title', 'Unknown Title'),
                "extracted_price": product_results.get('product_results', {}).get('extracted_price', None),
                "user_requested_time": product_results.get('search_metadata', {}).get('created_at', 'Unknown Time'),
                "brand": product_results.get('product_results', {}).get('brand', 'Unknown Brand')
            }
            x = collection.insert_one(document)
            print(f'Loaded some data please check{x}')
        except Exception as e:
            raise e
        
        finally:
            if client:
                client.close()
                print("MongoDB connection closed.")

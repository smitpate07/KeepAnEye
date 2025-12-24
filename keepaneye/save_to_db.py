from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from keepaneye.read_creds import AppConfig

class SaveToDB:
    """
    Class to handle saving product data to MongoDB
    """
    def __init__(self):
        """
        Initialize database connection configuration
        """
        try:
            self.config = AppConfig()
            self.db_uri = f"mongodb+srv://{self.config.DATABASE_USER}:{self.config.DATABASE_PASSWORD}@cluster0.25acfan.mongodb.net/?appName=Cluster0"

        except Exception as e:
            raise e
    
    def save_product_data(self, api_results, asin):
        """
        Extract product data from API results and save to MongoDB
        
        Args:
            api_results: Dictionary containing API response
            asin: Product ASIN
        
        Returns:
            dict: The document that was saved
        """
        try:
            # Extract relevant data from API results
            product_info = api_results.get('product_results', {})
            item_spec = api_results.get('item_specifications', {})
            
            if not product_info:
                print("✗ No product information found in API results")
                return None
            
            # Get price - it's already a float in 'extracted_price'
            price = product_info.get('extracted_price', 0)
            
            # If extracted_price is not available, try to parse from 'price' string
            if price == 0 and 'price' in product_info:
                price_str = product_info.get('price', '$0')
                try:
                    # Remove '$' and convert to float
                    price = float(price_str.replace('$', '').replace(',', ''))
                except:
                    price = 0
            
            # Get brand - check both locations
            brand = item_spec.get('brand', product_info.get('brand', 'N/A'))
            
            # Get stock - it's already a string
            stock = product_info.get('stock', 'Unknown')
            
            # Prepare document for MongoDB
            document = {
                'asin': asin,
                'title': product_info.get('title', 'N/A'),
                'extracted_price': price,
                'stock': stock,
                'brand': brand,
                'user_requested_time': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            # Save to MongoDB
            self._insert_to_mongodb(document)
            
            print(f"✓ Data saved to MongoDB")
            print(f"  - Title: {document['title'][:50]}...")
            print(f"  - Price: ${document['extracted_price']}")
            print(f"  - Stock: {document['stock']}")
            print(f"  - Brand: {document['brand']}")
            
            return document
            
        except Exception as e:
            print(f"✗ Error saving to database: {str(e)}")
            raise e
    
    def _insert_to_mongodb(self, document):
        """
        Insert document into MongoDB
        
        Args:
            document: Dictionary containing product data
        """
        try:
            # Connect to MongoDB
            client = MongoClient(self.db_uri, server_api=ServerApi('1'))
            database = client["AWS_TRACKER"]
            collection = database["AWS_TRACKER_PYTHON"]
            
            # Insert document
            collection.insert_one(document)
            
            # Close connection
            client.close()
            
        except Exception as e:
            raise Exception(f"MongoDB insertion error: {str(e)}")
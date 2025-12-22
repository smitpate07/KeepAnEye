from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from keepaneye.read_creds import AppConfig

class PriceMonitor:
    """
    Class to monitor price changes from MongoDB
    """
    def __init__(self):
        """
        Initialize price monitor with database connection
        """
        try:
            self.config = AppConfig()
            self.db_uri = f"mongodb+srv://{self.config.DATABASE_USER}:{self.config.DATABASE_PASSWORD}@cluster0.25acfan.mongodb.net/?appName=Cluster0"

        except Exception as e:
            raise e
        
    def check_price_changes(self, search_string, field_name='asin'):
        """
        Check for price changes in the database
        
        Args:
            search_string: Search term (e.g., ASIN)
            field_name: Field to search in (default: 'asin')
        
        Returns:
            dict: Dictionary containing price change information or None
                - price_dropped (bool): True if price dropped
                - product_data (dict): Product information if price dropped
        """
        try:
            # Connect to MongoDB
            client = MongoClient(self.db_uri, server_api=ServerApi('1'))
            database = client["AWS_TRACKER"]
            collection = database["AWS_TRACKER_PYTHON"]
            
            # Query the database
            query = {field_name: {"$regex": search_string, "$options": "i"}}
            results = collection.find(query)
            
            # Sort by timestamp (oldest to newest)
            data = sorted(results, key=lambda doc: datetime.strptime(doc['user_requested_time'], "%Y-%m-%d %H:%M:%S %Z"))
            
            if not data:
                print(f"ℹ️  No documents found matching '{search_string}'.")
                client.close()
                return None
            
            print(f"📊 Found {len(data)} record(s) for '{search_string}'")
            
            # If only one document exists, no comparison possible
            if len(data) == 1:
                doc = data[0]
                print(f"ℹ️  Only one record found - no price comparison available yet")
                print(f"  - Time: {doc['user_requested_time']}")
                print(f"  - Price: ${doc['extracted_price']}")
                client.close()
                return None
            
            # Compare only the latest document with the second-to-last (most recent vs previous)
            previous_doc = data[-2]  # Second most recent
            current_doc = data[-1]   # Most recent
            
            previous_price = previous_doc['extracted_price']
            current_price = current_doc['extracted_price']
            price_diff = current_price - previous_price
            
            print(f"\n💰 Price Comparison:")
            print(f"  Previous: ${previous_price} ({previous_doc['user_requested_time']})")
            print(f"  Current:  ${current_price} ({current_doc['user_requested_time']})")
            print(f"  Change:   ${price_diff:.2f}")
            
            # Prepare result
            result = {
                'price_dropped': False,
                'product_data': None
            }
            
            # Detect price changes
            if price_diff < 0:
                print(f"  ✓ Price change detected (Price DROPPED by ${abs(price_diff):.2f})")
                result['price_dropped'] = True
                result['product_data'] = {
                    'asin': current_doc['asin'],
                    'title': current_doc['title'],
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'price_drop': abs(price_diff),
                    'stock': current_doc.get('stock', 'Unknown'),
                    'brand': current_doc.get('brand', 'N/A')
                }
            elif price_diff > 0:
                print(f"  ✗ No price change detected (Price INCREASED by ${price_diff:.2f})")
            else:
                print(f"  → No price change (Price remained the same)")
            
            # Close the connection
            client.close()
            
            return result
            
        except Exception as e:
            print(f"✗ Error checking price: {str(e)}")
            if 'client' in locals():
                client.close()
            raise e
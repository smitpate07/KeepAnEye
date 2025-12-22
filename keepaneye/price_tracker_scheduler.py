import time
import schedule
from datetime import datetime
from keepaneye.user_input import UserInput
from keepaneye.api_call import ApiCall
from keepaneye.read_creds import AppConfig
from pymongo import MongoClient
from pymongo.server_api import ServerApi

class PriceTrackerScheduler:
    def __init__(self):
        """
        Initialize the price tracker scheduler
        """
        self.asin = None
        self.config = AppConfig()
        self.api_caller = None
        
    def get_user_input_once(self):
        """
        Get user input only once at the start
        """
        try:
            user_input = UserInput()
            self.asin = user_input.user_input
            print(f"\n✓ Tracking initiated for ASIN: {self.asin}")
            print(f"⏰ API calls will run every 12 hours")
            print(f"🕐 First call starting now...\n")
            return True
        except Exception as e:
            print(f"✗ Error getting user input: {str(e)}")
            return False
    
    def fetch_and_store_price(self):
        """
        Fetch price data from API and store in MongoDB
        """
        try:
            print(f"\n{'='*80}")
            print(f"🔍 Fetching price data for ASIN: {self.asin}")
            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}\n")
            
            # Create API caller instance with the stored ASIN
            api_caller = ApiCall(self.asin)
            
            # Fetch data from API
            results = api_caller.call_load()
            
            if not results:
                print("✗ No results returned from API")
                return
            
            # Extract relevant data
            product_info = results.get('product_result', {})
            
            if not product_info:
                print("✗ No product information found")
                return
            
            # Prepare document for MongoDB
            document = {
                'asin': self.asin,
                'title': product_info.get('title', 'N/A'),
                'extracted_price': product_info.get('prices', [{}])[0].get('value', 0),
                'stock': product_info.get('availability', {}).get('raw', 'Unknown'),
                'brand': product_info.get('brand', 'N/A'),
                'user_requested_time': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            # Store in MongoDB
            self.store_to_mongodb(document)
            
            print(f"✓ Price data fetched and stored successfully!")
            print(f"  - Title: {document['title'][:50]}...")
            print(f"  - Price: ${document['extracted_price']}")
            print(f"  - Stock: {document['stock']}")
            print(f"\n⏰ Next API call scheduled in 12 hours")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"✗ Error fetching/storing price: {str(e)}")
    
    def store_to_mongodb(self, document):
        """
        Store document to MongoDB
        
        Args:
            document: Dictionary containing product data
        """
        try:
            # Connect to MongoDB
            client = MongoClient(self.config.DB_URI, server_api=ServerApi('1'))
            database = client["AWS_TRACKER"]
            collection = database["AWS_TRACKER_PYTHON"]
            
            # Insert document
            collection.insert_one(document)
            
            # Close connection
            client.close()
            
        except Exception as e:
            raise Exception(f"MongoDB storage error: {str(e)}")
    
    def start_tracking(self):
        """
        Start the price tracking with 12-hour intervals
        """
        # Get user input once
        if not self.get_user_input_once():
            print("✗ Failed to initialize. Exiting...")
            return
        
        # Run the first API call immediately
        self.fetch_and_store_price()
        
        # Schedule the job to run every 12 hours
        schedule.every(12).hours.do(self.fetch_and_store_price)
        
        print(f"\n{'='*80}")
        print(f"🎯 Price Tracker is now running!")
        print(f"📊 Monitoring ASIN: {self.asin}")
        print(f"⏰ Updates every 12 hours")
        print(f"🛑 Press Ctrl+C to stop")
        print(f"{'='*80}\n")
        
        # Keep the script running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print(f"\n\n{'='*80}")
            print(f"🛑 Price Tracker stopped by user")
            print(f"{'='*80}\n")


if __name__ == '__main__':
    tracker = PriceTrackerScheduler()
    tracker.start_tracking()
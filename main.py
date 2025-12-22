import time
import schedule
from datetime import datetime
from keepaneye.user_input import UserInput
from keepaneye.api_call import ApiCall
from keepaneye.save_to_db import SaveToDB
from keepaneye.notify_user import NotifyUser

class AmazonPriceTracker:
    """
    Main orchestrator class for Amazon Price Tracker
    Handles user input, API calls, data storage, and notifications
    """
    def __init__(self):
        """
        Initialize the Amazon Price Tracker
        """
        self.asin = None
        self.db_handler = SaveToDB()
        self.notifier = NotifyUser()
        
    def get_user_input_once(self):
        """
        Get user input only once at the start
        """
        try:
            print(f"\n{'='*80}")
            print(f"🚀 Amazon Price Tracker - Starting...")
            print(f"{'='*80}\n")
            
            user_input = UserInput()
            self.asin = user_input.user_input
            
            print(f"\n{'='*80}")
            print(f"✓ Price Tracking Initiated")
            print(f"📦 ASIN: {self.asin}")
            print(f"⏰ API calls will run every 12 hours")
            print(f"📧 Email notifications enabled for price drops")
            print(f"{'='*80}\n")
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
            
            # Step 1: Create API caller and fetch data
            api_caller = ApiCall(self.asin)
            results = api_caller.call_load()
            
            if not results:
                print("✗ No results returned from API")
                return
            
            # Step 2: Save data to MongoDB
            print(f"\n💾 Saving data to Database...")
            saved_doc = self.db_handler.save_product_data(results, self.asin)
            
            if not saved_doc:
                print("✗ Failed to save data")
                return
            
            # Step 3: Check for price drops and send notification
            print(f"\n" + "="*80)
            self.notifier.check_and_notify(self.asin)
            
            print(f"\n⏰ Next API call scheduled in 12 hours")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"✗ Error in fetch_and_store_price: {str(e)}")
    
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
        print(f"📧 Email alerts enabled for price drops")
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
            print(f"📊 Final Status:")
            print(f"   - ASIN monitored: {self.asin}")
            print(f"   - Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}\n")


if __name__ == '__main__':
    tracker = AmazonPriceTracker()
    tracker.start_tracking()
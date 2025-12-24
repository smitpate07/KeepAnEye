from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from keepaneye.read_creds import AppConfig

class TrackingManager:
    """
    Manages product tracking subscriptions with email associations
    """
    def __init__(self):
        """
        Initialize tracking manager with database connection
        """
        try:
            self.config = AppConfig()
            self.db_uri = f"mongodb+srv://{self.config.DATABASE_USER}:{self.config.DATABASE_PASSWORD}@cluster0.25acfan.mongodb.net/?appName=Cluster0"

        except Exception as e:
            raise e
    
    def add_tracking(self, asin, email):
        """
        Add a new tracking subscription
        
        Args:
            asin: Product ASIN to track
            email: Email address to send notifications to
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            client = MongoClient(self.db_uri, server_api=ServerApi('1'))
            database = client["AWS_TRACKER"]
            collection = database["TRACKING_SUBSCRIPTIONS"]
            
            # Check if tracking already exists
            existing = collection.find_one({'asin': asin, 'email': email})
            
            if existing:
                # Update existing tracking
                collection.update_one(
                    {'asin': asin, 'email': email},
                    {'$set': {
                        'last_updated': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        'status': 'active'
                    }}
                )
            else:
                # Create new tracking subscription
                document = {
                    'asin': asin,
                    'email': email,
                    'created_at': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    'last_updated': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    'status': 'active'
                }
                collection.insert_one(document)
            
            client.close()
            return True
            
        except Exception as e:
            print(f"Error adding tracking: {str(e)}")
            return False
    
    def get_subscribers_for_asin(self, asin):
        """
        Get all email addresses subscribed to an ASIN
        
        Args:
            asin: Product ASIN
        
        Returns:
            list: List of email addresses
        """
        try:
            client = MongoClient(self.db_uri, server_api=ServerApi('1'))
            database = client["AWS_TRACKER"]
            collection = database["TRACKING_SUBSCRIPTIONS"]
            
            # Find all active subscriptions for this ASIN
            subscriptions = collection.find({'asin': asin, 'status': 'active'})
            emails = [sub['email'] for sub in subscriptions]
            
            client.close()
            return emails
            
        except Exception as e:
            print(f"Error getting subscribers: {str(e)}")
            return []
    
    def get_all_tracked_asins(self):
        """
        Get all ASINs being tracked
        
        Returns:
            list: List of unique ASINs
        """
        try:
            client = MongoClient(self.db_uri, server_api=ServerApi('1'))
            database = client["AWS_TRACKER"]
            collection = database["TRACKING_SUBSCRIPTIONS"]
            
            # Get all unique ASINs with active status
            asins = collection.distinct('asin', {'status': 'active'})
            
            client.close()
            return asins
            
        except Exception as e:
            print(f"Error getting tracked ASINs: {str(e)}")
            return []
    
    def remove_tracking(self, asin, email):
        """
        Remove a tracking subscription
        
        Args:
            asin: Product ASIN
            email: Email address
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            client = MongoClient(self.db_uri, server_api=ServerApi('1'))
            database = client["AWS_TRACKER"]
            collection = database["TRACKING_SUBSCRIPTIONS"]
            
            # Mark as inactive instead of deleting
            collection.update_one(
                {'asin': asin, 'email': email},
                {'$set': {
                    'status': 'inactive',
                    'last_updated': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }}
            )
            
            client.close()
            return True
            
        except Exception as e:
            print(f"Error removing tracking: {str(e)}")
            return False
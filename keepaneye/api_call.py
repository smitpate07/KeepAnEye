from keepaneye.read_creds import AppConfig 
from serpapi import GoogleSearch 

class ApiCall: 
    """
    Class to handle API calls to SerpAPI for Amazon product data
    """
    def __init__(self, asin_input): 
        """
        Initialize API call with ASIN
        
        Args:
            asin_input: Can be either a UserInput object or a string ASIN
        """
        try: 
            # Handle both UserInput object and direct string input
            if hasattr(asin_input, 'user_input'):
                # If it's a UserInput object
                self.asin = asin_input.user_input
            else:
                # If it's a direct string
                self.asin = asin_input
                
            self.__config = AppConfig() 
        except Exception as e: 
            raise e 
    
    def call_load(self): 
        """
        Make API call to fetch product data from Amazon
        
        Returns:
            dict: Product data from SerpAPI
        """
        try: 
            params = { 
                "engine": "amazon_product", 
                "asin": f"{self.asin}", 
                "api_key": f"{self.__config.API_KEY}" 
            } 
            
            print(f"🔍 Calling API for ASIN: {self.asin}")
            search = GoogleSearch(params) 
            results = search.get_dict() 
            
            if results:
                print(f"✓ API call successful")
            
            return results 
            
        except Exception as e: 
            print(f"✗ API call failed: {str(e)}")
            raise e
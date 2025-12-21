from keepaneye.user_input import UserInput
from keepaneye.read_creds import AppConfig 
from serpapi import GoogleSearch 
class ApiCall: 
    def __init__(self,user_input:UserInput): 
        try: 
            self.user_input = user_input 
            self.__config = AppConfig() 
        except Exception as e: 
            raise e 
    def call_load(self): 
        try: 
            params = { "engine": "amazon_product", 
                      "asin": f"{self.user_input}", 
                      "api_key": f"{self.__config.API_KEY}" } 
            search = GoogleSearch(params) 
            results = search.get_dict() 
            return results 
        except Exception as e: raise e
import requests
import json
import numpy as np

class GoogleAPI(object):
    """Class for retaining mean ratings of places by coordinates with radius"""
    def __init__(self, api):
        self.api = api
    
    def getting_ratings_by_coordinates(self, location, radius, types):
        """Function for gettting mean ratings of places"""
        
        # Web address at which we can get service of google maps API
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        # Parameteres to get data
        params = {
            'location': location,
            'radius': radius,
            'types': types,
            'key': self.api
        }
        
        # Sending request
        request = requests.get(endpoint_url, params)
        
        # Loading requested data in json file
        json_data = json.loads(request.content)     
        
        def overall_rating(x): 
            """Function in case there is no places in specific radius"""
            try: 
                return x['rating'] 
            except KeyError: 
                return None 
        
        # Mean of places
        mean_rating = np.mean([overall_rating(x) for x in json_data['results'] if overall_rating(x) is not None]) 

        return mean_rating

    
    def getting_price_level_by_coordinates(self, location, radius, types):
        
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        params = {
            'location': location,
            'radius': radius,
            'types': types,
            'key': self.api
        }

        request = requests.get(endpoint_url, params)

        json_data = json.loads(request.content)

        def price_level(x): 
            try: 
                return x['price_level'] 
            except KeyError: 
                return None 

        price_rating = np.mean([price_level(x) for x in json_data['results'] if price_level(x) is not None]) 

        return price_rating


    def getting_shopping_mall_by_coordinates(self, location, radius, types):
        
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        params = {
            'location': location,
            'radius': radius,
            'types': types,
            'key': self.api
        }

        request = requests.get(endpoint_url, params)

        json_data = json.loads(request.content)

        def shop_rating(x): 
            try: 
                return x['shopping_mall'] 
            except KeyError: 
                return None 

        shop_rating = np.mean([shop_rating(x) for x in json_data['results'] if shop_rating(x) is not None]) 

        return shop_rating

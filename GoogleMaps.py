# Using Python requests and the Google Maps Geocoding API.
#
# References:
#
# * http://docs.python-requests.org/en/latest/
# * https://developers.google.com/maps/

import requests

def get_info(**params):
    if 'address' not in params.keys():
        params['address'] = None
    params['sensor'] = 'false'
    params['key'] = 'AIzaSyAwkGbfmnJH4LVlFgcBcAxlFw5VswMe2Pc'
    
    # Do the request and get the response data
    req = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                       params=params)
    res = req.json()

    if 'results' in res.keys() and res['results']:
        # Use the first result
        result = res['results'][0]
        
        loc = result['geometry']['location']
        return result['formatted_address'], (loc['lat'], loc['lng'])

    else:
        return None

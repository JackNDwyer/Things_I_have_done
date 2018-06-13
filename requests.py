"""
Jazz API

Connects to the Jazz API
"""

import json
import requests


class Jazz(object):
   """ Jazz class """

   def __init__(self, token):
       self.api_token = token
       self.url = "https://api.resumatorapi.com/v1/"

   @property
   def applicants(self):
       """ Applicants property returns json """
       response = ''
       data = []
       for i in range(100):
               response = requests.get(self.url + 'applicants/page/' + str(i+1)+'/?apikey=' + self.api_token)
               if len(response.text) > 10:
                   data.extend(json.loads(response.text))
               else:
                   break
       return data

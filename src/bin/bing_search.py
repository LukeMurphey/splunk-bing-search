from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path
from bing_search_app.modular_input import Field, FieldValidationException, ModularInput, DurationField, IntegerField

#from bing_search_app.pws import google, bing
import requests
import time
import sys
import splunk
import json

class BingSearch(ModularInput):
    
    def __init__(self, timeout=30):

        scheme_args = {'title': "Bing Web Search",
                       'description': "Obtains results from Bing web search",
                       'use_external_validation': "true",
                       'streaming_mode': "xml",
                       'use_single_instance': "false"}
        
        args = [
                Field("key", "Bing API Key", "The Bing API key", empty_allowed=False),
                IntegerField("count", "Result Count", "The number of search results to return", empty_allowed=False),
                DurationField("interval", "Interval", "The interval defining how often to perform the check; can include time units (e.g. 15m for 15 minutes, 8h for 8 hours)", empty_allowed=False),
                Field("search", "Search", "The search to execute", none_allowed=False, empty_allowed=False, required_on_create=True, required_on_edit=True)
                ]
        
        ModularInput.__init__( self, scheme_args, args, logger_name='bing_search_modular_input' )
        
        if timeout > 0:
            self.timeout = timeout
        else:
            self.timeout = 30
         
    @classmethod
    def flatten(cls, item, dictionary=None, name=None):
        
        if dictionary is None:
            dictionary = {}
        
        if name is None:
            name = ""
        
        iterative_name = name
            
        if len(iterative_name) > 0:
            iterative_name = name + "."
        
        # Handle dictionaries
        if isinstance(item, dict):
            for key in item:
                cls.flatten(item[key], dictionary,  iterative_name + key)
        
        # Handle arrays
        elif not isinstance(item, basestring) and isinstance(item, (list, tuple)):
            
            index = 0
            
            for a in item:
                cls.flatten(a, dictionary, iterative_name + str(index))
                
                index = index + 1
                
                
        # Handle plain values
        elif item in [True, False, None]:
            dictionary[name] = item
            
        # Handle date
        elif item.__class__.__name__ == "struct_time":
            dictionary[name] = time.strftime('%Y-%m-%dT%H:%M:%SZ', item)
            
        # Handle string values
        else:
            dictionary[name] = str(item)
            
        return dictionary
            
    @staticmethod
    def get_api_key(session_key):
        """
        Perform a search against bing.
        
        Arguments:
        query -- The search to perform
        key -- The API key to use for obtaining the results
        search_type -- The type of the results to return. Should be one on of: search, news
        count -- The number of results
        offset -- The offset (the number of results to skip)
        """
        
        _, content = splunk.rest.simpleRequest('/servicesNS/nobody/bing_search/admin/conf-inputs/bing_search', sessionKey=session_key, getargs={'output_mode': 'json'})
        
        data = json.loads(content)
        
        if "key" in data['entry'][0]['content']:
            return data['entry'][0]['content']['key']
        else:
            return None
        
    @staticmethod
    def bing_search(query, key, search_type='search', count=10, offset=0, logger=None):
        """
        Perform a search against Bing. If the count is above 50, then it will iterate and keep calling Bing to get results until hitting the limit.
        
        Arguments:
        query -- The search to perform
        key -- The API key to use for obtaining the results
        search_type -- The type of the results to return. Should be one on of: search, news
        count -- The number of results
        offset -- The offset (the number of results to skip)
        """
        
        try:
            current_offset = offset
            left_to_get = count
            results = []
            
            # Keep looping, getting 50 results until we get all of the items
            while left_to_get > 0:
                
                # Determine the number of results to get
                if left_to_get > 50:
                    count_to_get = 50
                else:
                    count_to_get = left_to_get
                
                # Get the results
                results.extend(BingSearch.do_bing_search(query, key, search_type, count=count_to_get, offset=current_offset))
                
                # Update the offset
                current_offset = current_offset + count_to_get
                
                # Update the number to retrieve
                left_to_get = left_to_get - count_to_get
                
            # Return the results
            return results
        except Exception:
            if logger is not None:
                logger.exception("Exception")
        
    @staticmethod
    def do_bing_search(query, key, search_type='search', count=10, offset=0, return_raw_results=False):
        """
        Perform a search against bing.
        
        Arguments:
        query -- The search to perform
        key -- The API key to use for obtaining the results
        search_type -- The type of the results to return. Should be one on of: search, news
        count -- The number of results
        offset -- The offset (the number of results to skip)
        """
        
        # Make the URL (see https://dev.cognitive.microsoft.com/docs/services/56b43f72cf5ff8098cef380a/operations/56b449fbcf5ff81038d15cdf)
        url = 'https://api.cognitive.microsoft.com/bing/v5.0/' + search_type
        
        # Query string parameters
        payload = {
            'q': query,
            'count' : count,
            'offset' : offset
        }
        
        # Set the authentication header
        headers = {'Ocp-Apim-Subscription-Key': key}
        
        # Make the GET request
        results = requests.get(url, params=payload, headers=headers)
        
        # Get JSON response
        if return_raw_results:
            return results.json()
        else:
            
            r = results.json()
            
            # Get the entries
            entries = []
            
            # Handle web-pages
            if 'webPages' in r and 'value' in r['webPages']:
                for entry in r['webPages']['value']:
                    d = BingSearch.flatten(entry)
                    d['type'] = 'web-page'
                    entries.append(d)
                
            # Handle videos
            if 'videos' in r and 'value' in r['videos']:
                for entry in r['videos']['value']:
                    d = BingSearch.flatten(entry)
                    d['type'] = 'image'
                    entries.append(d)
        
            return entries
    
    def run(self, stanza, cleaned_params, input_config):
        
        # Make the parameters
        #interval         = cleaned_params["interval"]
        #title            = cleaned_params["title"]
        search           = cleaned_params["search"]
        count            = cleaned_params.get("count", 50)
        sourcetype       = cleaned_params.get("sourcetype", "bing_search")
        host             = cleaned_params.get("host", None)
        index            = cleaned_params.get("index", "default")
        source           = stanza
        
        # Get the API key
        api_key = BingSearch.get_api_key(input_config.session_key)
        
        if api_key is None:
            self.logger.warn("No Bing API key was provided, input will terminate")
            return
        
        #results = Bing.search(search, num=count)
        search_results = BingSearch.bing_search(search, api_key, logger=self.logger)
        
        for r in search_results:
            self.output_event(r, stanza, index=index, source=source, sourcetype=sourcetype, host=host, unbroken=True, close=True, encapsulate_value_in_double_quotes=True)
            
            
if __name__ == '__main__':
    
    bing_search = None
    try:
        bing_search = BingSearch()
        bing_search.execute()
        sys.exit(0)
    except Exception:
        if bing_search is not None and bing_search.logger is not None:
            bing_search.logger.exception("Unhandled exception was caught, this may be due to a defect in the script") # This logs general exceptions that would have been unhandled otherwise (such as coding errors)
        raise
from bing_search_app.search_command import SearchCommand
from bing_search import BingSearch as BingSearchInput
import sys

class BingSearch(SearchCommand):

    def __init__(self, query, offset=0, count=50, search_type="search"):

        # Save the parameters
        self.query = query
        self.offset = int(offset)
        self.count = int(count)
        self.search_type = search_type

        if query is None or len(query) == 0:
            raise Exception("No query was provided")

        # Initialize the class
        SearchCommand.__init__( self, run_in_preview=True, logger_name='bing_search_command')

    def handle_results(self, results, session_key, in_preview):

        # Log that we are getting started
        self.logger.info("Searching for q=%r", self.query)

        # Get the API key
        api_key = BingSearchInput.get_api_key(session_key)

        if api_key is None:
            raise Exception("No Bing API key defined; get an API key from Microsoft and enter the API key into the setup screen of the Bing search app; see http://bit.ly/2rIKR8h")

        # Perform the search
        results = BingSearchInput.bing_search(query=self.query, key=api_key, search_type=self.search_type, count=self.count, offset=self.offset, logger=self.logger)

        self.output_results(results)

if __name__ == '__main__':
    try:
        BingSearch.execute()
        sys.exit(0)
    except Exception as exception:
        print exception

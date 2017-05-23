================================================
Overview
================================================

This app provides a mechanism for pulling web search results from Bing. You can obtain results by using the included input or by running the "bingsearch" command from SPL like this:

    | bingsearch query="splunk apps"



================================================
Configuring Splunk
================================================

Install this app into Splunk by doing the following:

  1. Log in to Splunk Web and navigate to "Apps » Manage Apps" via the app dropdown at the top left of Splunk's user interface
  2. Click the "install app from file" button
  3. Upload the file by clicking "Choose file" and selecting the app
  4. Click upload
  5. Restart Splunk if a dialog asks you to

Once the app is installed, you can use the app by configuring a new input:
  1. Navigate to "Settings » Data Inputs" at the menu at the top of Splunk's user interface.
  2. Click "Bing Web Search"
  3. Click "New" to make a new instance of an input

You will need to obtain an API key from Microsoft. You can get a free key for up to 5,000 queries per month at https://datamarket.azure.com/dataset/bing/searchweb.



================================================
Getting Support
================================================

Go to the following website if you need support:

     http://splunk-base.splunk.com/apps/3355/answers/

You can access the source-code and get technical details about the app at:

     https://github.com/LukeMurphey/splunk-bing-search



================================================
Change History
================================================

+---------+------------------------------------------------------------------------------------------------------------------+
| Version |  Changes                                                                                                         |
+---------+------------------------------------------------------------------------------------------------------------------+
| 0.5     | Initial release                                                                                                  |
|---------|------------------------------------------------------------------------------------------------------------------|
| 0.6     | Updated the setup page to indicate where to get an API key                                                       |
|         | Added a README                                                                                                   |
+---------+------------------------------------------------------------------------------------------------------------------+

#!/usr/bin/python
"""
Google API to connect to the Google Analytics
"""

import httplib2
import os
from googleapiclient import discovery
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
import argparse
import urlparse
import sys

#sys.path.insert("etl_utilities")
import etl_utilities.date_util

"""A simple example of how to access the Google Analytics API."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def get_service(api_name, api_version, scopes, key_file_location):
   """Get a service that communicates to a Google API.

   Args:
       api_name: The name of the api to connect to.
       api_version: The api version to connect to.
       scopes: A list auth scopes to authorize for the application.
       key_file_location: The path to a valid service account JSON key file.

   Returns:
       A service that is connected to the specified API.
   """

   credentials = ServiceAccountCredentials.from_json_keyfile_name(
           key_file_location, scopes=scopes)

   # Build the service object.
   service = build(api_name, api_version, credentials=credentials)

   return service


def get_first_profile_id(service):
   # Use the Analytics service object to get the first profile id.

   # Get a list of all Google Analytics accounts for this user
   accounts = service.management().accounts().list().execute()

   if accounts.get('items'):
       # Get the first Google Analytics account.
       account = accounts.get('items')[0].get('id')

       # Get a list of all the properties for the first account.
       properties = service.management().webproperties().list(
               accountId=account).execute()

       if properties.get('items'):
           # Get the first property id.
           property = properties.get('items')[0].get('id')

           # Get a list of all views (profiles) for the first property.
           profiles = service.management().profiles().list(
                   accountId=account,
                   webPropertyId=property).execute()

           if profiles.get('items'):
               # return the first view (profile) id.
               return profiles.get('items')[0].get('id')

   return None


def get_results(service, profile_id, metrics, dimensions, start_date = '1daysAgo', end_date = 'today'):
   # Use the Analytics Service Object to query the Core Reporting API
   # for the number of sessions within the past seven days.
   return service.data().ga().get(
           ids='ga:' + profile_id,
           start_date = start_date,
           end_date = end_date,
           metrics = metrics, dimensions = dimensions).execute()


def print_results(results):
   # Print data nicely for the user.
   if results:
       print 'View (Profile):', results.get('profileInfo').get('profileName')
       print 'Total Sessions:', results.get('rows')[0][0]

   else:
       print 'No results found'


def main(key_file_location, metrics, dimensions, start_date, end_date):
   # Define the auth scopes to request.
   scope = 'https://www.googleapis.com/auth/analytics.readonly'
   #key_file_location = '<REPLACE_WITH_JSON_FILE>'

   # Authenticate and construct service.
   service = get_service(
           api_name='analytics',
           api_version='v3',
           scopes=[scope],
           key_file_location=key_file_location)

   profile_id = get_first_profile_id(service)
   return get_results(service, profile_id, metrics = metrics, dimensions  = dimensions, start_date = start_date, end_date = end_date)



def prepare_credentials(path, secret_path):
   """ retrieves crendentials from storage or refreshes the token """

   parser = argparse.ArgumentParser(parents=[tools.argparser])
   #flags = ""

   api_scopes = 'https://www.googleapis.com/auth/analytics.readonly'
   #this is the work around for the service account problem. google prefers service accounts for api calls, but because this is an old account,
   #we had to use a back door way. Basically retrieve client_secrets.json from the account that has access to the data, and the using the flow_from_clientsecrets
   #we authorize our account. If I'm not mistaken the flow call brings in a session_token.json from google
   client_secrets = path
   flow = flow_from_clientsecrets(client_secrets, scope=api_scopes, message='%s is missing' % client_secrets)

   # Retrieve existing credendials
   session_token = secret_path
   storage = Storage(session_token)
   credentials = storage.get()


   # If the steps fail, we use our json files to generate credentials
   if credentials is None or credentials.invalid:
       credentials = tools.run_flow(flow, storage)
   return credentials

def connect(path, secret_path):
   """ Creates an http object and authorize it using the function prepare_credentials()"""

   api_name = 'analytics'
   api_version = 'v3'

   http = httplib2.Http()
   credentials = prepare_credentials(path=path, secret_path = secret_path)
   http = credentials.authorize(http)

   # Build the Analytics Service Object with the authorized http object
   return discovery.build(api_name, api_version, http=http)

def google_analytics_data(service, dimensions, metrics, view_id, start_date, end_date):
   """
   fetches the Google Analytics Data
   The Google Analytics dimensions and metrics return in order: campaign, channel_grouping, date, medium, source, ad_clicks, bounces, goal_completions_all, new_users, page_views, session_duration, sessions
   """

   id = "ga:" + view_id
   google_data = {"rows": [], "sampled": "N"}

   # get Google Analytics data
   data = service.data().ga().get(ids=id, start_date=start_date, end_date=end_date,
                                  dimensions=dimensions, metrics=metrics, start_index=1, max_results='10000', samplingLevel = 'HIGHER_PRECISION').execute()

   # No GA data.  Return an empty list
   if data.get('rows') == None:
       return google_data

   if data.get('nextLink') == None:
       paginate = False
   else:
       paginate = True


   data_rows = []
   data_rows = data_rows + data['rows']

   # check for sampling
   if data['containsSampledData']:
       google_data["sampled"] = "Y"

   # paginating all the results until 'nextLink' doesn't appear in the report data
   while paginate:
       parameters = urlparse.parse_qs(urlparse.urlparse(data['nextLink']).query)

       # get Google Analytics data
       data = service.data().ga().get(ids=id, start_date=start_date, end_date=end_date,
                                      dimensions=dimensions, metrics=metrics,
                                      start_index=str(parameters['start-index'][0]), max_results='10000').execute()

       data_rows = data_rows + data['rows']

       # check for pagination
       if data.get('nextLink') == None:
           paginate = False

   google_data["rows"] = data_rows

   # return the dictionary with rows and sampling status
   return google_data

# def format_custom_dimension_column_for_row(google_data):
#     """
#     add custom dimension column to row or null if it doesn't exist
#     and then appends to the end of the array
#     """
#
#     for r in google_data["rows"]:
#         r.append(google_id)
#
#         # add empty/null column
#         r.append("")
#     return google_data["rows"]
#
# def format_events_date_for_row(google_id, google_data, load_date):
#     """
#     formats the event report date column from 20170130 to Redshift a compliant date format 2017-01-30
#     and then appends to the end of the array
#     """
#
#     for r in google_data["rows"]:
#         r[1] = str(r[1])[:4] + "-" + str(r[1][4:6]) + "-" + str(r[1][6:8])
#         r.append(google_id)
#
#         # add load date timestamp
#         r.append(load_date)
#     return google_data["rows"]
#
# def format_goals_date_for_row(google_id, google_data, load_date):
#     """
#     formats the goals report date column from 20170130 to Redshift a compliant date format 2017-01-30
#     and then appends to the end of the array
#     """
#
#     for r in google_data["rows"]:
#         r[2] = str(r[2])[:4] + "-" + str(r[2][4:6]) + "-" + str(r[2][6:8])
#         r.append(google_id)
#
#         # add load date timestamp
#         r.append(load_date)
#     return google_data["rows"]
#
# def format_metrics_date_session_for_row(google_id, google_data, load_date):
#     """
#     formats the metrics report date column from 20170130 to Redshift a compliant date format 2017-01-30
#     and also transforms the session duration column from a float to an integer then appends to the end of the array
#     """
#
#     for r in google_data["rows"]:
#         r[2] = str(r[2])[:4] + "-" + str(r[2][4:6]) + "-" + str(r[2][6:8])
#
#         # transforms any float to int for session_duration
#         r[10] = int(float(r[10]))
#
#         # adding the google account id to end of the row
#         r.append(google_id)
#
#         # add load date timestamp
#         r.append(load_date)
#     return google_data["rows"]
#
# def format_pages_date_for_row(google_id, load_date, google_data):
#     """
#     formats the goals report date column from 20170130 to Redshift a compliant date format 2017-01-30
#      and then appends to the end of the array
#     """
#
#     for r in google_data["rows"]:
#         # format nice Redshift date
#         r[0] = str(r[0])[:4] + "-" + str(r[0][4:6]) + "-" + str(r[0][6:8])
#
#         # transforms any float to int
#         r[9] = int(float(r[9]))
#         r[11] = int(float(r[11]))
#
#         # append client id and load date
#         r.append(google_id)
#         r.append(load_date)
#     return google_data["rows"]
#
# def format_source_medium_and_custom_dimenson_for_row(google_data, custom_dimenstion):
#     """ formats and splits sourceMedium into 2 columns """
#
#     for r in google_data["rows"]:
#         # split into source and medium
#         source_medium = r[5].split("/")
#
#         # chomp off totalEvents and uniqueEvents and add
#         # back after populating source and medium
#         total_event = r.pop()
#         unique_event = r.pop()
#
#      # populate medium field
#         r[5] = source_medium[1].strip()
#
#         # populate source field
#         r.append(source_medium[0].strip())
#
#         # set to null when custom dimension is not used
#         if custom_dimenstion == 'N':
#             r.append("")
#
#         # add back totalEvents and uniqueEvents
#         r.append(unique_event)
#         r.append(total_event)
#
#     return google_data["rows"]
#
# def format_unique_user_metrics_for_row(google_id, google_data, date_range, load_date):
#     """
#     formats the unique user metrics report date column from 20170130 to Redshift a compliant date format 2017-01-30
#     and also transforms the session duration column from a float to an integer then appends to the end of the array
#     appends the google id and date to end of row
#     """
#
#     for r in google_data["rows"]:
#         # transforms an float to int for session_duration
#         r[9] = int(float(r[9]))
#
#         # adding the google account id to end of the row
#         r.append(google_id)
#
#         # adding last month's ending date
#         r.append(date_range[1])
#
#         # adding sampled status
#         r.append(google_data["sampled"])
#
#         # adding load date
#         r.append(load_date)
#     return google_data["rows"]
#
# def format_unique_site_metrics_for_row(google_id, google_data, date_range, load_date):
#     """
#     formats the unique site metrics report date column from 20170130 to Redshift a compliant date format 2017-01-30
#     and also transforms the session duration column from a float to an integer then appends to the end of the array
#     appends the google id and date to end of row
#     """
#
#     for r in google_data["rows"]:
#         # transforms an float to int for session_duration
#         r[5] = int(float(r[5]))
#
#         # adding the google account id to end of the row
#         r.append(google_id)
#
#         # adding last month's ending date
#         r.append(date_range[1])
#
#         # adding sampled status
#         r.append(google_data["sampled"])
#
#         # adding load date
#         r.append(load_date)
#     return google_data["rows"]

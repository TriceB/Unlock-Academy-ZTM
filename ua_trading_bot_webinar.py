"""
This will will print the UUID of the past Black Box Trading Webinar
"""

import requests
import json
import pygsheets
import pandas as pd
from google.oauth2 import service_account
from datetime import datetime
import time
from urllib.parse import urljoin, urlparse, urlsplit

#   Get the current time when the code starts running
start_time = datetime.now()
#   Get the time elapsed - current time - start time

print("Start/Current Local Time --> " + str(time.ctime()))

#   ParseResult(
#   scheme='https',
#   netloc='api.zoom.us',
#   path='/v2/webinars/88377897916/registrants',
#   params='',
#   query='occurrence_id=<string>&status=approved&page_size=110&page_number=1',
#   fragment=''
#   )


url = "https://api.zoom.us/v2/webinars/88377897916/registrants?occurrence_id=<string>&status=approved&next_page_token="
# url = "https://api.zoom.us/v2/webinars/83249183441/registrants?occurrence_id=<string>&status=approved&next_page_token="

payload = {}
headers = {
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIaFZmRTRaTVNZTzloRUpGMkttenVRIiwiZXhwIjoxNjA2MTA0MjM5fQ.DnWPwA3qIvqdRUmVmSfyCA8G_I3rcLJkOXohKkUF2Rw',
  'Cookie': '_zm_lang=en-US; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_date_format=mm/dd/yy; cred=6C64DE3AE923E59D8E69DE88E8BD19B9'
}

response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text.encode('utf8'))

trading_bot_data = response.text.encode('utf8')
# print(response.text.encode('utf8'))
parsed_response = json.loads(trading_bot_data)
# print(parsed_response)

# next_page_token = parsed_response["next_page_token"]
# print(next_page_token)

#   If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


with open('credentials.json') as source:
    info = json.load(source)
credentials = service_account.Credentials.from_service_account_info(info)
#   authorize Python Sheets access to Google Sheets
client = pygsheets.authorize(service_account_file='credentials.json')

tbot_webinar_ids = ['88377897916', '83249183441']
next_page_token = parsed_response["next_page_token"]


def main():
    get_tbot_students()
    store_tbot_participants()

# def get_urls():
#     new_url = []
#     for ids in tbot_webinar_ids:
#         webinar_scheme_net = "https://api.zoom.us"
#     # for token in next_page_token:
#         print(next_page_token)
#         webinar_path = '/v2/webinars/' + str(ids) + '/participants?page_size=30&' + str(next_page_token) + '='
#         webinar_url_joined = urljoin(webinar_scheme_net, webinar_path)
#         new_url.append(webinar_url_joined)
#     return new_url
#
#
# print(get_urls())

#   TODO: figure out how pagination works
#    10/11 - currently pulling both meetings from the list above but only pulling 1 next page token
#    and attaching it to both ids


# def get_urls():
#     new_url = []
#     # for tokens in next_page_token:
#     webinar_scheme_net = "https://api.zoom.us"
#     # for token in next_page_token:
#     if next_page_token:
#         for token in next_page_token:
#             print(next_page_token)
#             webinar_path = '/v2/webinars/83249183441/participants?page_size=300&next_page_token=' + str(token)
#             webinar_url_joined = urljoin(webinar_scheme_net, webinar_path)
#             new_url.append(webinar_url_joined)
#         print(new_url)
#     # return new_url
#
#
# get_urls()


def get_tbot_students():
    participants = parsed_response["registrants"]
    # print(participants)
    student_email_name = []
    for participant in participants:
        # student_first_name = students["first_name"]
        # participant_last_name = participant["last_name"]
        # student_full_name = student_first_name + student_last_name
        # student_email = students["email"]
        # if student_last_name in participants:
        # if statement to check if there is a key named last_name
        if "last_name" in participant:
            student_info = participant["email"], participant["first_name"] + " " + participant["last_name"]
            student_email_name.append(student_info)
            # sort each member by name
            student_email_name.sort(key=lambda tup: tup[1])
            # print("if this prints, the if statement is true")
        else:
            student_info = participant["email"], participant["first_name"]
            student_email_name.append(student_info)
            # sort each member by the name
            student_email_name.sort(key=lambda tup: tup[1])
            # print("if this prints, the if statement is not true (printing the else)" + str(student_email_name))
    return student_email_name


# #   for each url created above, parse through the url then run the function to get the students
# for urls in get_urls():
#     response = requests.request("GET", urls, headers=headers, data=payload)
#     # print(response.text.encode('utf8'))
#     zoom_data = response.text.encode('utf8')
#     parsed_response = json.loads(zoom_data)
#     # print(parsed_response)


# get_tbot_students()

# print(get_tbot_students())


def store_tbot_participants():
    """
    Function to store all Trading Bot webinar participants in Google Sheets
    """
    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')
    #   create a new spreadsheet in the given folder
    tbot_participants_sheet = client.create(title="UA Trading Bot Participants",
                                            folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    tbot_wks = tbot_participants_sheet.add_worksheet("Participants")
    # tbot_wks.insert_rows(0, values=["Participant Email Address", "Participant Name"])
    tbot_df = pd.DataFrame(get_tbot_students(), columns=['Participant Email Address', 'Participant Name'])
    tbot_wks.set_dataframe(tbot_df, start=(1, 1), copy_index=False, copy_head=True)

    tbot_wks.cell("A1").set_text_format("bold", True)
    tbot_wks.cell("B1").set_text_format("bold", True)
#     # tbot_wks.cell("C1").set_text_format("bold", True)
#     tbot_participants = get_trading_bot_students()
#     for participant in tbot_participants:
#         participant_email = participant[0].lower()
#         participant_name = participant[1]
#         # participant_last_name = participant[2]
#         tbot_wks.insert_rows(1, values=[participant_email, participant_name])

    #   TODO: figure out if I can just make the end the last field in column B.
    #       if the above is not possible, get the last field through code (since this will change),
    #       then insert variable it below
    # tbot_wks.sort_range(start='A2', end='C110', basecolumnindex=1, sortorder='ASCENDING')
    tbot_df.sort_values(by='Participant Email Address', ascending=True)
    #   Share spreadsheet with read only access to anyone with the link
    tbot_participants_sheet.share('', role='reader', type='anyone')
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Trading Bot Participants List can be found here: ", tbot_participants_sheet.url)
    print("End/Current Local Time --> " + str(time.ctime()))
    time_elapsed = datetime.now() - start_time
    print("Trading Bot Participants Run Time --> " + str(time_elapsed))


# store_tbot_participants()

if __name__ == '__main__':
    main()

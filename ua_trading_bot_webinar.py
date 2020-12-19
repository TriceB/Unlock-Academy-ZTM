"""
This will will print the UUID of the past Black Box Trading Webinar
"""

import os
import requests
import json
import pygsheets
import pandas as pd
from google.oauth2 import service_account
from datetime import datetime, timedelta, date
import time
from pprint import pprint, pformat
import jwt
import http.client
# import datetime
import logging
from UnlockAcademyZTM.thinkific_members import get_members

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('manual_email_check.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

#   ParseResult(
#   scheme='https',
#   netloc='api.zoom.us',
#   path='/v2/webinars/88377897916/registrants',
#   params='',
#   query='occurrence_id=<string>&status=approved&page_size=110&page_number=1',
#   fragment=''
#   )


# url = "https://api.zoom.us/v2/webinars/88377897916/registrants"
#         # "https://api.zoom.us/v2/webinars/83249183441/registrants",
#         # "https://api.zoom.us/v2/webinars/81408245169/registrants"]


def connect_to_zoom(next_page_token=None):
    # Using PyJWT to create tokens
    # https://pyjwt.readthedocs.io/en/latest/usage.html#encoding-decoding-tokens-with-hs256

    # TODO: these will need to be safely stored in the db so that I can access them per client.
    api_key = str(os.environ.get('UA_ZOOM_API_KEY'))
    api_sec = str(os.environ.get('UA_ZOOM_API_SEC'))

    payload = {
        'iss': api_key,
        'exp': datetime.now() + timedelta(hours=10)
    }

    jwt_encoded = str(jwt.encode(payload, api_sec), 'utf-8')

    # print("TOKEN")
    # print(jwt_encoded)
    conn = http.client.HTTPSConnection("api.zoom.us")
    return conn, jwt_encoded


connection, jwt_token = connect_to_zoom()

headers = {
  'Authorization': 'Bearer %s' % jwt_token,
  'Cookie': '_zm_lang=en-US; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_date_format=mm/dd/yy; cred=6C64DE3AE923E59D8E69DE88E8BD19B9'
}


#   Scopes required for Google sheets. If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


with open('credentials.json') as source:
    info = json.load(source)
credentials = service_account.Credentials.from_service_account_info(info)
#   authorize Python Sheets access to Google Sheets
client = pygsheets.authorize(service_account_file='credentials.json')

tbot_webinar_ids = ['83249183441', '81408245169', '85347739061']    # '88377897916',  ID currently not working
# {'code': 3001, 'message': 'Meeting 88377897916 is not found or has expired.'}


def main():
    # just in case a sheet needs to be deleted
    # sh = client.open(title="UA Trading Bot Participants")
    # sh.delete()
    #   Get the current time when the code starts running

    start_time = datetime.now()
    print("Start/Current Local Time --> " + str(time.ctime()))
    #   Get the time elapsed - current time - start time

    for tbot_id in tbot_webinar_ids:
        get_web_reg(tbot_id)
    connect_to_zoom()

    get_tbot_students()
    time_elapsed = datetime.now() - start_time
    # logger.info(pformat(get_tbot_students()))
    print("Trading Bot Participants Run Time --> " + str(time_elapsed))

    store_tbot_participants()
    print("Store Trading Bot Participants Run Time --> " + str(time_elapsed))

    print("End/Current Local Time --> " + str(time.ctime()))


registrants = []


def get_web_reg(web_id=None, token_arg=None):
    base_url = "https://api.zoom.us/v2/webinars/"
    endpoint = "/registrants?status=approved"
    if not web_id:
        return False
    the_built_url = base_url + str(web_id) + endpoint
    if token_arg:
        the_built_url += '&next_page_token=' + str(token_arg)

    # Get the first page
    # print("web_id?", web_id)
    # print("token_arg?", token_arg)
    # print("built_url?", the_built_url)
    response = requests.request("GET", the_built_url, headers=headers)  # , payload=payload
    trading_bot_data = response.text.encode('utf8')
    parsed_response = json.loads(trading_bot_data)
    # print("parsed response ", parsed_response)
    # Pull out all of the registrants
    if parsed_response['registrants']:
        registrants.append(parsed_response['registrants'])
    token = parsed_response["next_page_token"]
    # logger.info(("some registrants ", registrants))
    # print("print token", token)
    if token:
        get_web_reg(web_id, token)
    return registrants


def get_tbot_students():
    thinkific_members = get_members()
    # print(thinkific_members[0])
    thinkific_member_emails = []
    for thinkific_email in thinkific_members:
        # print(thinkific_email[0])
        thinkific_member_emails.append(thinkific_email[0].lower())
    # logger.info("Thinkific emails")
    # logger.info(pformat(thinkific_member_emails))
    participants = registrants  # list structure - [  [{  }],  [{  }],  [{  }],  [{  }],  [{  }],  [{  }]  ]
    # pprint(participants)
    student_email_name = []
    for participant in participants:
        for student in participant:

            student_email = student["email"].lower()
            # logger.info("Zoom TBot emails")
            # logger.info(pformat(student_email))
            # Thinkific API requests are limited at 120 requests per minute.
            # run the code to check in the thinkific members but sleep for 1 minute between every 120 users
            # n = 120  # iterate over every 120th element
            # for i, x in enumerate(sample):
            #     if i % n == 0:
            #         print(i, x)
            #         time.sleep(10)
            #     else:
            #         print(i, x)
            # for i, thinkific_member_emails in enumerate(ua_members):
            #     if i % n == 0:

            # create a new list storing only the email addresses to check for existence later
            student_listing = []
            for person in student_email_name:
                student_listing.append(person['email'].lower())

            # check if email address is the thinkific members list (this means they are already a registered UA Student)
            if student_email not in thinkific_member_emails:
                # check for if email address already exists in new list
                if student_email not in student_listing:
                    # check if there is a last name included. If there is a last name include email, first name and last name
                    if "last_name" in student:
                        student_info = {"email": student_email, "first_name": student["first_name"], "last_name": student["last_name"]}
                        student_email_name.append(student_info)
                    # else if the user did not enter a last name when registering, only include the email and first name
                    else:
                        student_info = {"email": student_email, "first_name": student["first_name"]}
                        student_email_name.append(student_info)

                    # sleep for 60 secs to not reach request limit
                    # time.sleep(60)

    # student_email_name.sort(key=lambda tup: tup[1])
    student_email_name = sorted(student_email_name, key=lambda i: i['first_name'])

    # PREVIOUS CODE - used to before adding the code above to check in the thinkific members at the same time
    # if "last_name" in student:
    #     student_info = student["email"], student["first_name"] + " " + student["last_name"]
    #     if student_info not in student_email_name:  # remove exact duplicates (email and name match)
    #         # print("checking list --> ", student_email_name)
    #         if student_info[0] not in student_email_name:   # remove duplicates where the email already exists with different name
    #             # print("testing, testing -->", student_i,, nfo[0])
    #             student_email_name.append(student_info)
    #     # sort each member by name
    #     student_email_name.sort(key=lambda tup: tup[1])
    #     # print("if this prints, the if statement is true")
    # else:
    #     student_info = [student["email"], student["first_name"]]
    #     if student_info not in student_email_name:
    #         if student_info[0] not in student_email_name:
    #             student_email_name.append(student_info)
    #     # sort each member by the name
    #     student_email_name.sort(key=lambda tup: tup[1])
    #     # print("if this prints, the if statement is not true (printing the else)" + str(student_email_name))

    return student_email_name


def store_tbot_participants():
    """
    Function to store all Trading Bot webinar participants in Google Sheets
    """
    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')
    #   create a new spreadsheet in the given folder
    today = date.today()
    tbot_participants_sheet = client.create(title="UA Trading Bot Participants " + str(today),
                                            folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    # create a new worksheet in the spreadsheet named "Participants"
    tbot_wks = tbot_participants_sheet.add_worksheet("Participants")

    students_not_members = get_tbot_students()
    # turn the students info into a dataframe to load into Google Sheets
    tbot_df = pd.DataFrame(students_not_members)     # , columns=['Participant Email Address', 'Participant First Name', 'Participant Last Name']

    # start entering the data in the sheet at row 1, column 1
    tbot_wks.set_dataframe(tbot_df, start=(1, 1), copy_index=False, copy_head=True)
    # change NaN values to blanks - for registrants who did not enter a last name
    tbot_wks.replace("NaN", replacement="", matchEntireCell=True)
    # bold text format for headers
    tbot_wks.cell("A1").set_text_format("bold", True)
    tbot_wks.cell("B1").set_text_format("bold", True)
    tbot_wks.cell("C1").set_text_format("bold", True)
    # sort sheet by email addresses
    tbot_df.sort_values(by='email', ascending=True)

    #   Share spreadsheet with read only access to anyone with the link
    tbot_participants_sheet.share('', role='reader', type='anyone')
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Trading Bot Participants List can be found here: ", tbot_participants_sheet.url)


if __name__ == '__main__':
    main()

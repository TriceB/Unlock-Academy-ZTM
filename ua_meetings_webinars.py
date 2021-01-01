"""
Get registrants from all meetings/webinars
# webinar types 5 or 9 - get all instances of trading bot webinars
# meeting types 2 or 8
# want to get anybody who's attended any UA Zooms
# tag topic to the attendee to show what meeting/webinar they attended

How to get all the registrants from all meetings/webinars
# List Meeting Registrants
# store meetings in new variable in function for registrants
# loop through and get registrants
# {email, first name, last name, meeting topic}
"""

import os
import json
from datetime import datetime, timedelta, date
from pprint import pprint, pformat
import jwt
import http.client
import logging
import requests
import pygsheets
import pandas as pd
from google.oauth2 import service_account

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('meetings_webinars_check1.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

#   Scopes required for Google sheets. If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


with open('credentials.json') as source:
    info = json.load(source)
credentials = service_account.Credentials.from_service_account_info(info)
#   authorize Python Sheets access to Google Sheets
client = pygsheets.authorize(service_account_file='credentials.json')


def main():
    connect_to_zoom()
    # get_all_zoom_users()
    get_all_zoom_meetings()
    # get_all_zoom_webinars()
    # get_ids()
    # for webinar_id in webinar_ids:
    #     get_web_reg(webinar_id)
    # print(list_of_meetings)
    meetings_with_registrants = []
    for meeting in list_of_meetings:
        # print(meeting)
        meeting_type = meeting["meeting_type"]
        if meeting_type == 8:
            meetings_with_registrants.append(meeting["meeting_id"])
    # print(meetings_with_registrants)
    for meeting_id in meetings_with_registrants:
        get_meeting_reg(meeting_id)
    print(meetings_with_registrants)

    # store_webinar_registrants()
    

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
    
    print("TOKEN")
    print(jwt_encoded)
    conn = http.client.HTTPSConnection("api.zoom.us")
    return conn, jwt_encoded


connection, jwt_token = connect_to_zoom()

headers = {
    'Authorization': 'Bearer %s' % jwt_token,
    'Cookie': '_zm_lang=en-US; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_date_format=mm/dd/yy; cred=6C64DE3AE923E59D8E69DE88E8BD19B9'
}


# base_url = "https://api.zoom.us"


def get_all_zoom_users():
    """
    Function to return a list of dicts of all UA Zoom users (hosts)
    Get all users
    https://marketplace.zoom.us/docs/api-reference/zoom-api/users/users
    """
    connect = http.client.HTTPSConnection("api.zoom.us")
    base_url = "/v2/users?status=active&page_size=30"
    connect.request("GET", base_url, headers=headers)
    res = connect.getresponse()
    data = res.read()
    # pprint(data.decode("utf-8"))
    parsed_data = json.loads(data)
    # pprint(parsed_data)
    list_of_users = parsed_data["users"]
    # print("the users", list_of_users)
    ua_user = []
    for users in list_of_users:
        # for all users in the list_of_users pull only First Name, Last Name, User Department, and User ID
        user = {"first_name": users["first_name"], "last_name": users["last_name"], "user_dept": users["dept"],
                "user_id": users["id"]}
        ua_user.append(user)
    # print("the users in the get users function")
    # pprint(ua_user)
    
    return ua_user


list_of_meetings = []


def get_all_zoom_meetings(token_arg=None):
    """
    Function to return a list of dicts of all UA meetings with type 2 or 8
    "Meeting Types:
    `1` - Instant meeting.
    `2` - Scheduled meeting.
    `3` - Recurring meeting with no fixed time.
    `8` - Recurring meeting with fixed time.",
    Meetings by user
    https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetings
    Past meetings
    https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/pastmeetings
    Meeting Registrants
    https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetingregistrants
    Meeting Participants
    https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/pastmeetingparticipants
    """
    connect = http.client.HTTPSConnection("api.zoom.us")
    users = get_all_zoom_users()
    # user_ids = []
    # print(users)
    # list_of_meetings = []
    for user_id in users:
        the_id = user_id["user_id"]
        # print("The IDS")
        # print(the_id)
        # user_ids.append(the_id)
        base_url = "/v2/users/" + the_id + "/meetings"
        # if there is a token, add it to the url string
        if token_arg:
            base_url += '&next_page_token=' + str(token_arg)
        
        connect.request("GET", base_url, headers=headers)
        res = connect.getresponse()
        data = res.read()
        # pprint(data.decode("utf-8"))
        parsed_data = json.loads(data)
        
        # pprint(parsed_data)
        meetings = parsed_data["meetings"]
        # loop through each meeting
        for meeting in meetings:
            # for each meeting, get the meeting type
            meeting_type = meeting["type"]
            # check if the meeting is type 2 or type 8
            if meeting_type == 2 or meeting_type == 8:
                # if meeting matches criteria, create a new dict with topic, id, uuid, host id, and meeting type
                meeting_info = {"meeting_topic": meeting["topic"],
                                "meeting_id": meeting["id"],
                                "meeting_uuid": meeting["uuid"],
                                "host_id": meeting["host_id"],
                                "meeting_type": meeting["type"]}
                # append each meeting info to empty list
                list_of_meetings.append(meeting_info)
                
        token = parsed_data["next_page_token"]
        if token:
            get_all_zoom_meetings(token)
    # print("The Meetings")
    # pprint(list_of_meetings)
    # list_of_users = parsed_data["users"]
    # print("the users", list_of_users)
    
    return list_of_meetings


list_of_webinars = []


def get_all_zoom_webinars(token_arg=None):
    """
    Function to return a list of dicts of all webinars hosted by users in
    EdTech department (Currently only Antoine.Digital)
    For all webinars listed, only return webinars of type 5 or 9
    Webinar Types:
    `5` - Webinar.
    `6` - Recurring webinar with no fixed time.
    `9` - Recurring webinar with a fixed time.
    Get all webinars
    https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinars
    Past Webinar Instances
    https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/pastwebinars
    Webinar Registrants
    https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/webinarregistrants
    """
    connect = http.client.HTTPSConnection("api.zoom.us")
    users = get_all_zoom_users()
    # user_ids = []
    
    # list_of_webinars = []
    for user_id in users:
        # loop through all users and get the user dept
        user_dept = user_id["user_dept"]
        # print("the user department", user_dept)
        # check all users to see if they are in the EdTech department
        if user_dept == "EdTech":
            # if the user is in the EdTech department, pull their user id
            the_id = user_id["user_id"]
            # append the user id to the empty list
            # user_ids.append(the_id)
            # concatenate the user id in the url string to only pull webinars that
            # users in the EdTech department have hosted
            base_url = "/v2/users/" + the_id + "/webinars"
            if token_arg:
                base_url += '&next_page_token=' + str(token_arg)
            
            connect.request("GET", base_url, headers=headers)
            res = connect.getresponse()
            data = res.read()
            # pprint(data.decode("utf-8"))
            parsed_data = json.loads(data)
            token = parsed_data["next_page_token"]
            # pprint(parsed_data)
            webinars = parsed_data["webinars"]
            # loop through all of the webinars
            for webinar in webinars:
                # store the type for each webinar
                webinar_type = webinar["type"]
                # check if the webinar is type 5 or 9
                if webinar_type == 5 or webinar_type == 9:
                    # if webinar matches criteria, create a new dict with topic, id, uuid, host id, and webinar type
                    webinar_info = {"webinar_topic": webinar["topic"], "webinar_id": webinar["id"],
                                    "webinar_uuid": webinar["uuid"], "host_id": webinar["host_id"],
                                    "webinar_type": webinar["type"]}
                    # append each webinar to empty list
                    list_of_webinars.append(webinar_info)
            if token:
                get_all_zoom_meetings(token)
    print("The Webinars")
    pprint(list_of_webinars)
    # list_of_users = parsed_data["users"]
    # print("the users", list_of_users)
    
    return list_of_webinars


meeting_ids = []
webinar_ids = []


def get_ids():
    
    ua_meetings = get_all_zoom_meetings()
    for meeting in ua_meetings:
        # meeting_id_topic = {"meeting_id": meeting["meeting_id"], "meeting_topic": meeting["meeting_topic"]}
        meeting_id = meeting["meeting_id"]
        meeting_ids.append(meeting_id)
    
    ua_webinars = get_all_zoom_webinars()
    for webinar in ua_webinars:
        webinar_id = webinar["webinar_id"]
        webinar_ids.append(webinar_id)
    
    return meeting_ids, webinar_ids


def get_web_reg(web_id=None, token_arg=None):
    """
        Function to loop through all webinar IDs and return a list dicts with
        email, first_name, last_name, webinar_topic, webinar_id
        """
    registrants = []
    
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
        for webinar in list_of_webinars:
            for registrant in parsed_response['registrants']:
                # print(registrant)
                if "last_name" in registrant:
                    webinar_registrant_info = {"email": registrant["email"],
                                               "first_name": registrant["first_name"],
                                               "last_name": registrant["last_name"],
                                               "webinar_topic": webinar["webinar_topic"],
                                               "webinar_id": webinar["webinar_id"]}
                    registrants.append(webinar_registrant_info)
                else:
                    webinar_registrant_info = {"email": registrant["email"],
                                               "first_name": registrant["first_name"],
                                               "webinar_topic": webinar["webinar_topic"],
                                               "webinar_id": webinar["webinar_id"]
                                               }
                    registrants.append(webinar_registrant_info)
        # print(10 * "*" + " SOME WEBINAR REGISTRANTS " + 10 * "*" + " --> ")
        # pprint(registrants)
    token = parsed_response["next_page_token"]
    # print("print token", token)
    if token:
        get_web_reg(web_id, token)
    return registrants


def get_meeting_reg(meet_id=None, token_arg=None):
    """
    Function to loop through all meeting IDs and return a list dicts with
    email, first_name, last_name, meeting_topic, meeting_id
    """
    registrants = []
    # "/v2/meetings/81483069736/registrants?next_page_token=iWbzXWx6sPv2Zb5n6DdhKZvmFeArfLrodb2&page_size=30&status=approved"
    base_url = "https://api.zoom.us/v2/meetings/"
    endpoint = "/registrants?status=approved"
    if not meet_id:
        return False
    the_built_url = base_url + str(meet_id) + endpoint
    if token_arg:
        the_built_url += '&next_page_token=' + str(token_arg)
    
    # Get the first page
    # print("token_arg?", token_arg)
    # print("built_url?", the_built_url)
    response = requests.request("GET", the_built_url, headers=headers)  # , payload=payload
    trading_bot_data = response.text.encode('utf8')
    parsed_response = json.loads(trading_bot_data)
    # print("parsed response ", parsed_response)
    # Pull out all of the registrants
    if parsed_response['registrants']:
        for registrant in parsed_response['registrants']:
            # TODO: some meetings don't have registrants. check for participants instead
            
            if "last_name" in registrant:
                meeting_registrant_info = {"email": registrant["email"],
                                           "first_name": registrant["first_name"],
                                           "last_name": registrant["last_name"],
                                           # "meeting_topic": meeting["meeting_topic"],
                                           "meeting_id": meet_id}
                registrants.append(meeting_registrant_info)
            else:
                meeting_registrant_info = {"email": registrant["email"],
                                           "first_name": registrant["first_name"],
                                           # "meeting_topic": meeting["meeting_topic"],
                                           "meeting_id": meet_id}
                registrants.append(meeting_registrant_info)
    
        # pprint(registrants)
    token = parsed_response["next_page_token"]
    
    # print("print token", token)
    if token:
        get_meeting_reg(meet_id, token)
    return registrants


def store_webinar_registrants():
    """
    Function to store all Webinar registrants in Google Sheets
    """
    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')
    #   create a new spreadsheet in the given folder
    today = date.today()
    webinar_registrants_sheet = client.create(title="UA Webinar Registrants " + str(today),
                                              folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    # create a new worksheet in the spreadsheet named "Participants"
    webinar_registrants_wks = webinar_registrants_sheet.add_worksheet("Registrants")

    webinar_registrants = get_web_reg()
    # turn the students info into a dataframe to load into Google Sheets
    webinar_registrants_df = pd.DataFrame(webinar_registrants)     # , columns=['Participant Email Address', 'Participant First Name', 'Participant Last Name']

    # start entering the data in the sheet at row 1, column 1
    webinar_registrants_wks.set_dataframe(webinar_registrants_df, start=(1, 1), copy_index=False, copy_head=True)
    # change NaN values to blanks - for registrants who did not enter a last name
    webinar_registrants_wks.replace("NaN", replacement="", matchEntireCell=True)
    # bold text format for headers
    webinar_registrants_wks.cell("A1").set_text_format("bold", True)
    webinar_registrants_wks.cell("B1").set_text_format("bold", True)
    webinar_registrants_wks.cell("C1").set_text_format("bold", True)
    webinar_registrants_wks.cell("D1").set_text_format("bold", True)
    webinar_registrants_wks.cell("E1").set_text_format("bold", True)
    # sort sheet by email addresses
    webinar_registrants_df.sort_values(by='email', ascending=True)

    #   Share spreadsheet with read only access to anyone with the link
    webinar_registrants_sheet.share('', role='reader', type='anyone')
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Webinar Registrants List can be found here: ", webinar_registrants_sheet.url)
    
    
if __name__ == '__main__':
    main()

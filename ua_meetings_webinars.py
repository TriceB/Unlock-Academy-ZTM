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
import time
from pprint import pprint, pformat
from collections import OrderedDict
import jwt
import http.client
import logging
import requests
import pygsheets
import pandas as pd
from google.oauth2 import service_account
# from UnlockAcademyZTM.thinkific_members import get_members


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('webinars_check2.log')
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
    start_date_time = datetime.now()
    start_time = time.perf_counter()
    print("Start/Current Local Time --> " + str(time.ctime()) + " Perf counter " + str(time.perf_counter()))
    
    connect_to_zoom()
    get_all_zoom_users()
    get_all_zoom_meetings()
    get_all_zoom_webinars()
    # get_ids()
    
    time_elapsed = datetime.now() - start_date_time
    first_timer = time.perf_counter()
    print("Connection, Get Users, Meetings & Webinars Run Time --> " + str(first_timer))
    
    list_of_webinar_ids = []
    for webinar in list_of_webinars:
        web_id = webinar["webinar_id"]
        web_topic = webinar["webinar_topic"]
        webinar_id_topic = {"webinar_id": web_id,
                            "webinar_topic": web_topic}
        list_of_webinar_ids.append(webinar_id_topic)
    
    for webinar in list_of_webinar_ids:
        get_web_reg(webinar["webinar_id"], webinar["webinar_topic"])
        get_webinar_instances(webinar["webinar_id"], webinar["webinar_topic"])

    # print("Webinar Registrants")
    # pprint(list_of_webinar_registrants)
    
    web_registrants_and_instances_time = time.perf_counter()
    print("Get Webinar Registrants & Instances Run Time --> " + str(web_registrants_and_instances_time) +
          " Current Total Time --> " + str(web_registrants_and_instances_time - start_time))
    
    # print("list of webinar IDs")
    # pprint(list_of_webinar_ids)
    # print("list of webinar Instances")
    # pprint(list_of_webinar_instances)
    
    # print("The List of meetings")
    # pprint(list_of_meetings)
    
    meetings_with_registrants = []
    for meeting in list_of_meetings:
        # print(meeting)
        meeting_type = meeting["meeting_type"]
        if meeting_type == 8:
            meeting_id = meeting["meeting_id"]
            meeting_topic = meeting["meeting_topic"]
            meeting_id_topic = {"meeting_id": meeting_id,
                                "meeting_topic": meeting_topic
                                }
            meetings_with_registrants.append(meeting_id_topic)
    # pprint(meetings_with_registrants)
    for meeting in meetings_with_registrants:
        get_meeting_reg(meeting["meeting_id"], meeting["meeting_topic"])
    # print(meetings_with_registrants)

    # print("Meeting Registrants")
    # pprint(list_of_meeting_registrants)

    meeting_reg_time = time.perf_counter()
    print("Get Meeting Registrants Run Time --> " + str(meeting_reg_time) +
          " Current Total Time --> " + str(meeting_reg_time - start_time))

    meetings_with_participants = []
    for meeting in list_of_meetings:
        # print(meeting)
        meeting_type = meeting["meeting_type"]
        if meeting_type == 2 or meeting_type == 8:
            meeting_id = meeting["meeting_id"]
            meeting_topic = meeting["meeting_topic"]
            meeting_uuid = meeting["meeting_uuid"]
            meeting_id_topic = {"meeting_id": meeting_id,
                                "meeting_topic": meeting_topic,
                                "meeting_uuid": meeting_uuid
                                }
            meetings_with_participants.append(meeting_id_topic)
    # print("meetings with participants")
    # pprint(meetings_with_participants)

    for meeting in meetings_with_participants:
        get_meeting_instances(meeting["meeting_id"], meeting["meeting_topic"])

    # print("LIST OF MEETING INSTANCES")
    # pprint(list_of_meeting_instances)

    meeting_instances_time = time.perf_counter()
    print("Get Meeting Instances Run Time --> " + str(meeting_instances_time) +
          " Current Total Time --> " + str(meeting_instances_time - start_time))

    for meeting in list_of_meeting_instances:
        # print("A MEETING")
        # print(meeting)
        if "meeting_instances" in meeting:
            for instance in meeting["meeting_instances"]:
                # print("AN INSTANCE")
                # print(instance)
                # print(meeting["meeting_instances"])
                get_meeting_participants(meeting["meeting_id"], instance, meeting["meeting_topic"])
                # test_get_participants(meeting["meeting_id"], instance, meeting["meeting_topic"])

    # print("Meeting Participants")
    # pprint(list_of_meeting_participants)

    meeting_participants_time = time.perf_counter()
    print("Get Meeting Participants Run Time --> " + str(meeting_participants_time) +
          " Current Total Time --> " + str(meeting_participants_time - start_time))

    for webinar in list_of_webinar_instances:
        # print("A webinar")
        # print(webinar)
        if "webinar_instances" in webinar:
            for instance in webinar["webinar_instances"]:
                # print("AN INSTANCE")
                # print(instance)
                # print(webinar["webinar_instances"])
                get_webinar_participants(webinar["webinar_id"], instance, webinar["webinar_topic"])

    webinar_participants_time = time.perf_counter()
    print("Get Webinar Participants Run Time --> " + str(webinar_participants_time) +
          " Current Total Time --> " + str(webinar_participants_time - start_time))
    
    # print("Webinar Participants")
    # pprint(list_of_webinar_participants)
    
    # get_non_members()
    # print("Non Members")
    # pprint(list_of_non_members)
    
    store_meetings_webinars()
    store_webinar_registrants()
    store_webinar_participants()
    store_meeting_registrants()
    store_meeting_participants()
    
    store_data_time = time.perf_counter()
    print("Store Data to Google Sheets Run Time --> " + str(store_data_time) +
          " Current Total Time --> " + str(store_data_time - start_time))
    
    total_time_elapsed = time.perf_counter() - start_time
    print("End/Current Local Time --> " + str(time.ctime()) +
          " Total Run Time --> " + str(total_time_elapsed))
    

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
            base_url += '?next_page_token=' + str(token_arg)
        
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


# TODO: How to get participants from past meeting instances in order to use the UUID instead of the ID
#  If using past meeting instances - "/v2/past_meetings/89177533762/instances"
#  How do I pick which UUID to use
#  Using the first UUID - this will only work for meetings that only produce 1 past uuid
#  Using the last UUID - should be more accurate
#  currently creating a dict with meeting information
#  In the dict, for meeting ID, create a list of UUIDs
#  use negative indexing to pull that last uuid from the list uuids for each meeting

list_of_meeting_instances = []


def get_meeting_instances(meet_id=None, meet_topic=None, token_arg=None):
    """
    Function to return a list of all past (ended) meeting instances
    Zoom Meetings all generate a new UUID upon meeting creation and after meetings have ended.
    Each ended meeting, will create a new UUID which must be used to get the participants
    Using the first UUID, generated when the meeting is created will not pull the participants correctly
    https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/pastmeetings
    """
    base_url = "https://api.zoom.us/v2/past_meetings/"
    endpoint = "/instances?status=approved"
    if not meet_id:
        return False
    the_built_url = base_url + str(meet_id) + endpoint
    if token_arg:
        the_built_url += '&next_page_token=' + str(token_arg)
    
    # Get the first page
    # print("token_arg?", token_arg)
    # print("built_url?", the_built_url)
    response = requests.request("GET", the_built_url, headers=headers)  # , payload=payload
    meetings_data = response.text.encode('utf8')
    parsed_response = json.loads(meetings_data)
    meetings = parsed_response["meetings"]
    # print("parsed response for meeting ID - " + str(meet_id))
    # print(parsed_response)
    # print(len(parsed_response["meetings"]))
    # if parsed_response['meetings}']:
    meeting_instance = {"meeting_id": meet_id,
                        "meeting_topic": meet_topic,
                        
                        }
    uuids_list = []
    for meeting in meetings:
        # print(meeting)
        # currently creating a new list for every uuid in meetings
        # TODO: try making a list above, separately, then just iterating over the list if instead of all meetings
        uuids_list.append(meeting["uuid"])
    # if "uuid" in meeting:
        if len(parsed_response["meetings"]) == 1:
            # list_of_uuids = [meeting["uuid"]]
            meeting_instance["meeting_instances"] = uuids_list
            
            # meeting_instance["meeting_instances"] = meeting["uuid"]
            # list_of_meeting_instances.append(meeting_instance)
# else:
#     for meeting in meetings:
#
#         list_of_meeting_instances[0]["meeting_instance"]["meeting_instances"].append(meeting["uuid"])
#             # meeting_instance["meeting_instances"].append(meeting["uuid"])
        elif len(parsed_response["meetings"]) > 1:
            # print("MORE THAN 1 UUID")
            # uuids_list = []
            # print([meeting["uuid"]])
            # for uuid in meetings:
            #     print(uuid["uuid"])
            #     uuids_list.append(uuid["uuid"])
            # print(uuids_list)
            meeting_instance["meeting_instances"] = uuids_list
            # meeting_instance = {"meeting_id2": meet_id,
            #                     "meeting_topic": meet_topic,
            #                     "meeting_instances": uuids_list
            #                     }
    list_of_meeting_instances.append(meeting_instance)
    
    return list_of_meeting_instances


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
                base_url += '?next_page_token=' + str(token_arg)
            # print("GET ZOOM WEBINARS URL")
            # print(base_url)
            connect.request("GET", base_url, headers=headers)
            res = connect.getresponse()
            data = res.read()
            # pprint(data.decode("utf-8"))
            parsed_data = json.loads(data)
            token = parsed_data["next_page_token"]
            # pprint(parsed_data)
            # print("Get Webinars Next Page Token")
            # pprint(token)
            webinars = parsed_data["webinars"]
            # pprint(webinars)
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
                get_all_zoom_webinars(token)
    # print("The Webinars")
    # pprint(list_of_webinars)
    # logger.info(pformat(list_of_webinars))
    # list_of_users = parsed_data["users"]
    # print("the users", list_of_users)
    
    return list_of_webinars


list_of_webinar_instances = []


def get_webinar_instances(web_id=None, web_topic=None, token_arg=None):
    """
    Function to return a list of all past (ended) webinar instances
    Zoom webinars all generate a new UUID upon webinar creation and after webinars have ended.
    Each ended webinar, will create a new UUID which must be used to get the participants
    Using the first UUID, generated when the webinar is created will not pull the participants correctly
    https://marketplace.zoom.us/docs/api-reference/zoom-api/webinars/pastwebinars
    """
    base_url = "https://api.zoom.us/v2/past_webinars/"
    endpoint = "/instances?status=approved"
    if not web_id:
        return False
    the_built_url = base_url + str(web_id) + endpoint
    if token_arg:
        the_built_url += '&next_page_token=' + str(token_arg)
    
    # Get the first page
    # print("token_arg?", token_arg)
    # print("built_url?", the_built_url)
    response = requests.request("GET", the_built_url, headers=headers)  # , payload=payload
    webinar_data = response.text.encode('utf8')
    parsed_response = json.loads(webinar_data)
    webinars = parsed_response["webinars"]
    # print("parsed response for webinar ID - " + str(web_id))
    # print(parsed_response)
    # print(len(parsed_response["webinars"]))
    # if parsed_response['webinars}']:
    webinar_instance = {"webinar_id": web_id,
                        "webinar_topic": web_topic
                        }
    uuids_list = []
    for webinar in webinars:
        # print(webinar)
        # currently creating a new list for every uuid in webinars
        # TODO: try making a list above, separately, then just iterating over the list if instead of all webinars
        uuids_list.append(webinar["uuid"])
        # if "uuid" in webinar:
        if len(parsed_response["webinars"]) == 1:
            # list_of_uuids = [webinar["uuid"]]
            webinar_instance["webinar_instances"] = uuids_list
            
            # webinar_instance["webinar_instances"] = webinar["uuid"]
            # list_of_webinar_instances.append(webinar_instance)
        # else:
        #     for webinar in webinars:
        #
        #         list_of_webinar_instances[0]["webinar_instance"]["webinar_instances"].append(webinar["uuid"])
        #             # webinar_instance["webinar_instances"].append(webinar["uuid"])
        elif len(parsed_response["webinars"]) > 1:
            # print("MORE THAN 1 UUID")
            # uuids_list = []
            # print([webinar["uuid"]])
            # for uuid in webinars:
            #     print(uuid["uuid"])
            #     uuids_list.append(uuid["uuid"])
            # print(uuids_list)
            webinar_instance["webinar_instances"] = uuids_list
            # webinar_instance = {"webinar_id2": web_id,
            #                     "webinar_topic": web_topic,
            #                     "webinar_instances": uuids_list
            #                     }
    list_of_webinar_instances.append(webinar_instance)
    
    return list_of_webinar_instances


meeting_ids = []
webinar_ids = []


# def get_ids():
#
#     ua_meetings = get_all_zoom_meetings()
#     for meeting in ua_meetings:
#         # meeting_id_topic = {"meeting_id": meeting["meeting_id"], "meeting_topic": meeting["meeting_topic"]}
#         meeting_id = meeting["meeting_id"]
#         meeting_ids.append(meeting_id)
#
#     ua_webinars = get_all_zoom_webinars()
#     for webinar in ua_webinars:
#         webinar_id = webinar["webinar_id"]
#         webinar_ids.append(webinar_id)
#
#     return meeting_ids, webinar_ids


list_of_webinar_registrants = []


def get_web_reg(web_id=None, web_topic=None, token_arg=None):
    """
        Function to loop through all webinar IDs and return a list dicts with
        email, first_name, last_name, webinar_topic, webinar_id
        """
    
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
    webinars_data = response.text.encode('utf8')
    parsed_response = json.loads(webinars_data)
    # print("parsed response ", parsed_response)
    # Pull out all of the registrants
    # registrant_emails_list = []
    if parsed_response['registrants']:
        # for webinar in list_of_webinars:
        for registrant in parsed_response['registrants']:
            # print(registrant)
            registrant_email = registrant["email"].lower()
            # for person in list_of_webinar_participants:
            #     registrant_emails_list.append(person["email"].lower())
            # if registrant_email not in registrant_emails_list:
            if "last_name" in registrant:
                webinar_registrant_info = {"email": registrant_email,
                                           "first_name": registrant["first_name"],
                                           "last_name": registrant["last_name"],
                                           "webinar_id": web_id,
                                           "webinar_topic": web_topic
                                           }
                list_of_webinar_registrants.append(webinar_registrant_info)
            else:
                webinar_registrant_info = {"email": registrant_email,
                                           "first_name": registrant["first_name"],
                                           "webinar_id": web_id,
                                           "webinar_topic": web_topic
                                           }
                list_of_webinar_registrants.append(webinar_registrant_info)
        # print(10 * "*" + " SOME WEBINAR REGISTRANTS " + 10 * "*" + " --> ")
        # logger.info(pformat(registrants))
        # pprint(list_of_webinar_registrants)
    #     568541974, 674016059, 386270599 webinar IDs do not have any registrants
    token = parsed_response["next_page_token"]
    # print("print token", token)
    if token:
        get_web_reg(web_id, web_topic, token)
    return list_of_webinar_registrants


list_of_webinar_participants = []


def get_webinar_participants(web_id=None, web_instance=None, web_topic=None, token_arg=None):
    """
    Function to loop through all webinar IDs with participants
    instead of registrants and return a list dicts with
    email, first_name, last_name, webinar_topic, webinar_id
    """
    
    # TODO: In Zoom API for GET webinar Participants, both webinarId and webinarUUID work to get participants
    #  one will return a blank data set or an error, while the other will return participants
    #  How do I know which will work to actually get participants??
    
    base_url = "https://api.zoom.us/v2/report/webinars/"
    endpoint = "/participants?status=approved"
    if not web_instance:
        return False
    the_built_url = base_url + str(web_instance) + endpoint
    if token_arg:
        the_built_url += '&next_page_token=' + str(token_arg)
    # print("ZOOM URL - " + str(the_built_url))
    # Get the first page
    # print("token_arg?", token_arg)
    # print("built_url?", the_built_url)
    response = requests.request("GET", the_built_url, headers=headers)  # , payload=payload
    # get the response back for each webinar ID to find out which IDs are being processed fine and which do not exist
    if response.status_code == 200:
        print(str(web_id) + " - Success")
        
        past_webinars_data = response.text.encode('utf8')
        parsed_response = json.loads(past_webinars_data)
        # pprint(parsed_response)
        # participant_emails_list = []
        # Pull out all of the participants
        if parsed_response['participants']:
            for participant in parsed_response['participants']:
                
                # store the email in lower case
                participant_email = participant["user_email"].lower()
                # for person in list_of_webinar_participants:
                #     participant_emails_list.append(person["email"].lower())
                
                # print(str(web_id) + " Student Emails - " + str(student_emails_list))
                # print("Participant email - BEFORE IF " + str(participant_email))
                # split name field in order to get the first and last name separated
                participant_name_split = participant["name"].split(maxsplit=1)
                # for student in list_of_webinar_participants:
                #     student_emails_list.append(student["email"].lower())
                # print(participant_name_split)
                # TODO: figure out how to check for duplicates for each webinar NOT duplicates within the whole list
                #  ex. student 1 has attended webinar 101, 202, and 303
                #  student 1 joined webinar 303 3 times and is listed 3 times with the same email address for webinar 303
                #  student 1 should only be in the overall list 3 times (1 listing per webinar attended)
                #  [{"name": student 1, "webinar": 101}, {"name": student 1, "webinar": 202}, {"name": student 1, "webinar": 303}]
                #  currently student 1 is being listed 6 times
                #  (5 times - 1 listing for webinar 101, 202 and 303 + 2 extra times they joined webinar 303)
                #  [{"name": student 1, "webinar": 101}, {"name": student 1, "webinar": 202},
                #   {"name": student 1, "webinar": 303}, {"name": student 1, "webinar": 303}, {"name": student 1, "webinar": 303}]
                # if participant_email not in student_emails_list:
                # print("*** Participant email - AFTER IF *** " + str(participant_email))
                # if participant_email not in participant_emails_list:
                if len(participant_name_split) > 1:
                    participant_first_name = participant_name_split[0]
                    participant_last_name = participant_name_split[1]
                    # if "last_name" in participant:
                    webinar_participant_info = {"email": participant_email,
                                                "first_name": participant_first_name,
                                                "last_name": participant_last_name,
                                                "webinar_id": web_id,
                                                "webinar_topic": web_topic,
                                                "webinar_instance": web_instance
                                                }
                    list_of_webinar_participants.append(webinar_participant_info)
                else:
                    participant_first_name = participant_name_split[0]
                    webinar_participant_info = {"email": participant_email,
                                                "first_name": participant_first_name,
                                                "webinar_id": web_id,
                                                "webinar_topic": web_topic,
                                                "webinar_instance": web_instance
                                                }
                    list_of_webinar_participants.append(webinar_participant_info)
        # print("webinar Participants")
        # pprint(list_of_webinar_participants)
        if parsed_response["next_page_token"]:
            token = parsed_response["next_page_token"]
            
            # print("print token", token)
            if token:
                get_webinar_participants(web_id, web_instance, web_topic, token)
    elif response.status_code == 404:
        print(str(web_id) + " - Response Returned HTTP Status Code 404: There was an error getting webinar information.")
    return list_of_webinar_participants


list_of_meeting_registrants = []


def get_meeting_reg(meet_id=None, meet_topic=None, token_arg=None):
    """
    Function to loop through all meeting IDs and return a list dicts with
    email, first_name, last_name, meeting_topic, meeting_id
    """
    # for meeting in list_of_meetings:
    #     meeting_id = meeting["meeting_id"]
    #     meeting_topic = meeting["meeting_topic"]
        
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
    meetings_data = response.text.encode('utf8')
    parsed_response = json.loads(meetings_data)
    # print("parsed response ", parsed_response)
    # Pull out all of the registrants
    # registrant_emails_list = []
    if parsed_response['registrants']:
        for registrant in parsed_response['registrants']:
            # TODO: some meetings don't have registrants. check for participants instead
            
            registrant_email = registrant["email"].lower()
            
            # for person in list_of_meeting_registrants:
            #     registrant_emails_list.append(person["email"].lower())
            # logger.info("the email list")
            # logger.info(meet_id)
            # logger.info(registrant_emails_list)
            # if registrant_email not in registrant_emails_list:
            if "last_name" in registrant:
                meeting_registrant_info = {"email": registrant_email,
                                           "first_name": registrant["first_name"],
                                           "last_name": registrant["last_name"],
                                           "meeting_id": meet_id,
                                           "meeting_topic": meet_topic}
                list_of_meeting_registrants.append(meeting_registrant_info)
            else:
                meeting_registrant_info = {"email": registrant_email,
                                           "first_name": registrant["first_name"],
                                           "meeting_id": meet_id,
                                           "meeting_topic": meet_topic}
                list_of_meeting_registrants.append(meeting_registrant_info)
            # elif registrant_email in registrant_emails_list:
            #     logger.info("already in email list")
            #     logger.info(meet_id)
            #     logger.info(registrant_email)
        # pprint(list_of_meeting_registrants)
    token = parsed_response["next_page_token"]
    
    # print("print token", token)
    if token:
        get_meeting_reg(meet_id, meet_topic, token)
    return list_of_meeting_registrants


list_of_meeting_participants = []


def get_meeting_participants(meet_id=None, meet_instance=None, meet_topic=None, token_arg=None):
    """
    Function to loop through all meeting IDs with participants
    instead of registrants and return a list dicts with
    email, first_name, last_name, meeting_topic, meeting_id
    """

    # TODO: In Zoom API for GET Meeting Participants, both meetingId and meetingUUID work to get participants
    #  one will return a blank data set or an error, while the other will return participants
    #  How do I know which will work to actually get participants??
    
    base_url = "https://api.zoom.us/v2/past_meetings/"
    endpoint = "/participants"
    if not meet_instance:
        return False
    the_built_url = base_url + str(meet_instance) + endpoint
    if token_arg:
        the_built_url += '?next_page_token=' + str(token_arg)
    # print("ZOOM URL - " + str(the_built_url))
    # Get the first page
    # print("token_arg?", token_arg)
    # print("built_url?", the_built_url)
    response = requests.request("GET", the_built_url, headers=headers)  # , payload=payload
    # get the response back for each Meeting ID to find out which IDs are being processed fine and which do not exist
    if response.status_code == 200:
        print(str(meet_id) + " - Success")
    
        past_meetings_data = response.text.encode('utf8')
        parsed_response = json.loads(past_meetings_data)
        # pprint(parsed_response)
        token = parsed_response["next_page_token"]
        # Pull out all of the participants
        # participant_emails_list = []
        if parsed_response['participants']:
            for participant in parsed_response['participants']:
                
                # store the email in lower case
                participant_email = participant["user_email"].lower()
                # for person in list_of_meeting_participants:
                #     participant_emails_list.append(person["email"].lower())
                
                # student_emails_list.append(participant_email)
                # print(str(meet_id) + " Student Emails - " + str(student_emails_list))
                # print("Participant email - BEFORE IF " + str(participant_email))
                # split name field in order to get the first and last name separated
                participant_name_split = participant["name"].split(maxsplit=1)
                # for student in list_of_meeting_participants:
                #     student_emails_list.append(student["email"].lower())
                # print(participant_name_split)
                # TODO: figure out how to check for duplicates for each meeting NOT duplicates within the whole list
                #  ex. student 1 has attended meeting 101, 202, and 303
                #  student 1 joined meeting 303 3 times and is listed 3 times with the same email address for meeting 303
                #  student 1 should only be in the overall list 3 times (1 listing per meeting attended)
                #  [{"name": student 1, "meeting": 101}, {"name": student 1, "meeting": 202}, {"name": student 1, "meeting": 303}]
                #  currently student 1 is being listed 6 times
                #  (5 times - 1 listing for meeting 101, 202 and 303 + 2 extra times they joined meeting 303)
                #  [{"name": student 1, "meeting": 101}, {"name": student 1, "meeting": 202},
                #   {"name": student 1, "meeting": 303}, {"name": student 1, "meeting": 303}, {"name": student 1, "meeting": 303}]
                # if participant_email not in student_emails_list:
                # print("*** Participant email - AFTER IF *** " + str(participant_email))
                # if participant_email not in participant_emails_list:
                if len(participant_name_split) > 1:
                    participant_first_name = participant_name_split[0]
                    participant_last_name = participant_name_split[1]
                    # if "last_name" in participant:
                    meeting_participant_info = {"email": participant_email,
                                                "first_name": participant_first_name,
                                                "last_name": participant_last_name,
                                                "meeting_id": meet_id,
                                                "meeting_topic": meet_topic,
                                                "meeting_instance": meet_instance
                                                }
                    list_of_meeting_participants.append(meeting_participant_info)
                else:
                    participant_first_name = participant_name_split[0]
                    meeting_participant_info = {"email": participant_email,
                                                "first_name": participant_first_name,
                                                "meeting_id": meet_id,
                                                "meeting_topic": meet_topic,
                                                "meeting_instance": meet_instance
                                                }
                    list_of_meeting_participants.append(meeting_participant_info)
        # print("Meeting Participants")
        # pprint(list_of_meeting_participants)
        
        # print("print token", token)
        if token:
            get_meeting_participants(meet_id, meet_instance, meet_topic, token)
    elif response.status_code == 404:
        print(str(meet_id) + " - Response Returned HTTP Status Code 404: There was an error getting meeting information.")
    return list_of_meeting_participants


test_list_of_meeting_participants = dict()


def test_get_participants(meet_id=None, meet_instance=None, meet_topic=None, token_arg=None):
    """
    Testing code help from Coach Mike before adding to main code
    """
    base_url = "https://api.zoom.us/v2/past_meetings/"
    endpoint = "/participants?status=approved"
    if not meet_instance:
        return False
    the_built_url = base_url + str(meet_instance) + endpoint
    if token_arg:
        the_built_url += '?next_page_token=' + str(token_arg)
    print("ZOOM URL - " + str(the_built_url))
    # Get the first page
    # print("token_arg?", token_arg)
    # print("built_url?", the_built_url)
    response = requests.request("GET", the_built_url, headers=headers)  # , payload=payload
    # get the response back for each Meeting ID to find out which IDs are being processed fine and which do not exist
    if response.status_code == 200:
        print(str(meet_id) + " - Success")

        past_meetings_data = response.text.encode('utf8')
        parsed_response = json.loads(past_meetings_data)
        # pprint(parsed_response)

        # Pull out all of the registrants
        if parsed_response['participants']:
            for participant in parsed_response['participants']:
                participant_email = participant["user_email"].lower()
                # check if the email field is blank - blanks become a catch-all for all meetings
                # if
                if participant["user_email"] != "":
                    # split name field in order to get the first and last name separate
                    participant_name_split = participant["name"].split(maxsplit=1)
                    if len(participant_name_split) > 1:
                        # store the split name
                        participant_first_name = participant_name_split[0]
                        participant_last_name = participant_name_split[1]
                        # check if the email address already exists in the dict to make sure it's not a duplicate
                        if test_list_of_meeting_participants.get(participant_email) is None:
                            # create an ordered dict
                            user_data = OrderedDict()
                            user_data["email"] = participant_email
                            # add first_name key with participant_first_name as the value
                            user_data['first_name'] = participant_first_name
                            # add last_name key with participant_last_name as the value
                            user_data['last_name'] = participant_last_name
                            # create a new dict for meetings to store one or more meetings in later
                            user_data['meetings'] = dict()
                            # fill in the meetings key with dict of meeting id and topic as values
                            user_data['meetings'] = {
                                "id1": meet_id,
                                "topic": meet_topic
                            }
                            # store the user data into test_list_of_meeting_participants dict using the email as the dict key
                            test_list_of_meeting_participants[participant_email] = user_data
                        # else, if the participant_email is not None, the participant_email already exists as a key in the dict
                        # elif list_of_meeting_participants[participant_email]['meetings'][meet_id] is None:
                        else:
                            # store the dict of meeting id and meeting topic in a new dict using the meeting id as the key
                            test_list_of_meeting_participants[participant_email]['meetings'][meet_id] = {
                                "id2": meet_id,
                                "topic": meet_topic
                            }
                            # update the test_list_of_meeting_participants with the new dict created above
                            # test_list_of_meeting_participants[participant_email].update(test_list_of_meeting_participants[participant_email]['meetings'][meet_id])
    elif response.status_code == 404:
        print(str(meet_id) + " - Response Returned HTTP Status Code 404: There was an error getting meeting information.")
    # print("Coach Mike's test")
    # pprint(test_list_of_meeting_participants)
    return test_list_of_meeting_participants


def store_meetings_webinars():
    """
    Function to store all Meetings & Webinars in Google Sheets
    """
    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')
    #   create a new spreadsheet in the given folder
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    meetings_webinar_sheet = client.create(title="UA Meetings & Webinars " + str(report_date_time),
                                           folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    # create a new worksheet in the spreadsheet named "Registrants"
    meetings_wks = meetings_webinar_sheet.add_worksheet("Meetings")
    webinars_wks = meetings_webinar_sheet.add_worksheet("Webinars")
    
    # webinar_registrants = get_web_reg()
    # turn the students info into a dataframe to load into Google Sheets
    webinars_df = pd.DataFrame(list_of_webinars)  # , columns=['Participant Email Address', 'Participant First Name', 'Participant Last Name']
    meetings_df = pd.DataFrame(list_of_meetings)
    
    # start entering the data in the sheet at row 1, column 1
    webinars_wks.set_dataframe(webinars_df, start=(1, 1), copy_index=False, copy_head=True, escape_formulae=True)
    meetings_wks.set_dataframe(meetings_df, start=(1, 1), copy_index=False, copy_head=True, escape_formulae=True)
    
    # change NaN values to blanks - for registrants who did not enter a last name
    webinars_wks.replace("NaN", replacement="", matchEntireCell=True)
    meetings_wks.replace("NaN", replacement="", matchEntireCell=True)
    
    # bold text format for headers
    webinars_wks.cell("A1").set_text_format("bold", True)
    webinars_wks.cell("B1").set_text_format("bold", True)
    webinars_wks.cell("C1").set_text_format("bold", True)
    webinars_wks.cell("D1").set_text_format("bold", True)
    webinars_wks.cell("E1").set_text_format("bold", True)

    meetings_wks.cell("A1").set_text_format("bold", True)
    meetings_wks.cell("B1").set_text_format("bold", True)
    meetings_wks.cell("C1").set_text_format("bold", True)
    meetings_wks.cell("D1").set_text_format("bold", True)
    meetings_wks.cell("E1").set_text_format("bold", True)
    
    # sort sheet by meeting/webinar topic
    webinars_wks.sort_range(start='A2', end='F10000', basecolumnindex=0, sortorder='ASCENDING')
    meetings_wks.sort_range(start='A2', end='F10000', basecolumnindex=0, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    meetings_webinar_sheet.share('', role='reader', type='anyone')
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Meetings & Webinars List can be found here: ", meetings_webinar_sheet.url)


def store_webinar_registrants():
    """
    Function to store all Webinar registrants in Google Sheets
    """
    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')
    #   create a new spreadsheet in the given folder
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    webinar_registrants_sheet = client.create(title="UA Webinar Registrants " + str(report_date_time),
                                              folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    # create a new worksheet in the spreadsheet named "Registrants"
    webinar_registrants_wks = webinar_registrants_sheet.add_worksheet("Registrants")

    # webinar_registrants = get_web_reg()
    # turn the students info into a dataframe to load into Google Sheets
    webinar_registrants_df = pd.DataFrame(list_of_webinar_registrants)     # , columns=['Participant Email Address', 'Participant First Name', 'Participant Last Name']

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
    webinar_registrants_wks.sort_range(start='A2', end='F10000', basecolumnindex=0, sortorder='ASCENDING')

    #   Share spreadsheet with read only access to anyone with the link
    webinar_registrants_sheet.share('', role='reader', type='anyone')
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Webinar Registrants List can be found here: ", webinar_registrants_sheet.url)


def store_webinar_participants():
    """
    Function to store all Webinar Participants in Google Sheets
    """
    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')
    #   create a new spreadsheet in the given folder
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    webinar_participants_sheet = client.create(title="UA Webinar Participants " + str(report_date_time),
                                               folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    # create a new worksheet in the spreadsheet named "participants"
    webinar_participants_wks = webinar_participants_sheet.add_worksheet("Participants")
    
    # webinar_participants = get_web_reg()
    # turn the students info into a dataframe to load into Google Sheets
    webinar_participants_df = pd.DataFrame(list_of_webinar_participants)  # , columns=['Participant Email Address', 'Participant First Name', 'Participant Last Name']
    
    # start entering the data in the sheet at row 1, column 1
    webinar_participants_wks.set_dataframe(webinar_participants_df, start=(1, 1), copy_index=False, copy_head=True, escape_formulae=True)
    
    # change NaN values to blanks - for participants who did not enter a last name
    webinar_participants_wks.replace("NaN", replacement="", matchEntireCell=True)
    
    # bold text format for headers
    webinar_participants_wks.cell("A1").set_text_format("bold", True)
    webinar_participants_wks.cell("B1").set_text_format("bold", True)
    webinar_participants_wks.cell("C1").set_text_format("bold", True)
    webinar_participants_wks.cell("D1").set_text_format("bold", True)
    webinar_participants_wks.cell("E1").set_text_format("bold", True)
    
    # sort sheet by email addresses
    webinar_participants_wks.sort_range(start='A2', end='F10000', basecolumnindex=0, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    webinar_participants_sheet.share('', role='reader', type='anyone')
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Webinar Participants List can be found here: ", webinar_participants_sheet.url)


def store_meeting_registrants():
    """
    Function to store all Meeting registrants in Google Sheets
    """
    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')
    #   create a new spreadsheet in the given folder
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    meeting_registrants_sheet = client.create(title="UA Meeting Registrants " + str(report_date_time),
                                              folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    # create a new worksheet in the spreadsheet named "Registrants"
    meeting_registrants_wks = meeting_registrants_sheet.add_worksheet("Registrants")
    
    meeting_registrants = list_of_meeting_registrants
    
    # turn the students info into a dataframe to load into Google Sheets
    meeting_registrants_df = pd.DataFrame(meeting_registrants)  # , columns=['Participant Email Address', 'Participant First Name', 'Participant Last Name']
    
    # start entering the data in the sheet at row 1, column 1
    meeting_registrants_wks.set_dataframe(meeting_registrants_df, start=(1, 1), copy_index=False, copy_head=True)
    
    # change NaN values to blanks - for registrants who did not enter a last name
    meeting_registrants_wks.replace("NaN", replacement="", matchEntireCell=True)
    
    # bold text format for headers
    meeting_registrants_wks.cell("A1").set_text_format("bold", True)
    meeting_registrants_wks.cell("B1").set_text_format("bold", True)
    meeting_registrants_wks.cell("C1").set_text_format("bold", True)
    meeting_registrants_wks.cell("D1").set_text_format("bold", True)
    meeting_registrants_wks.cell("E1").set_text_format("bold", True)
    
    # sort sheet by email addresses
    meeting_registrants_wks.sort_range(start='A2', end='F10000', basecolumnindex=0, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    meeting_registrants_sheet.share('', role='reader', type='anyone')
    
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Meeting Registrants List can be found here: ", meeting_registrants_sheet.url)


def store_meeting_participants():
    """
    Function to store all Meeting participants in Google Sheets
    """
    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')
    #   create a new spreadsheet in the given folder
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    meeting_participants_sheet = client.create(title="UA Meeting Participants " + str(report_date_time),
                                               folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    # create a new worksheet in the spreadsheet named "Registrants"
    meeting_participants_wks = meeting_participants_sheet.add_worksheet("Participants")
    
    meeting_participants = list_of_meeting_participants
    
    # turn the students info into a dataframe to load into Google Sheets
    meeting_participants_df = pd.DataFrame(meeting_participants)  # , columns=['Participant Email Address', 'Participant First Name', 'Participant Last Name']
    
    # start entering the data in the sheet at row 1, column 1
    meeting_participants_wks.set_dataframe(meeting_participants_df, start=(1, 1), copy_index=False, copy_head=True, escape_formulae=True)
    
    # change NaN values to blanks - for registrants who did not enter a last name
    meeting_participants_wks.replace("NaN", replacement="", matchEntireCell=True)
    
    # bold text format for headers
    meeting_participants_wks.cell("A1").set_text_format("bold", True)
    meeting_participants_wks.cell("B1").set_text_format("bold", True)
    meeting_participants_wks.cell("C1").set_text_format("bold", True)
    meeting_participants_wks.cell("D1").set_text_format("bold", True)
    meeting_participants_wks.cell("E1").set_text_format("bold", True)
    
    # sort sheet by email addresses
    meeting_participants_wks.sort_range(start='A2', end='F10000', basecolumnindex=0, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    meeting_participants_sheet.share('', role='reader', type='anyone')
    
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Meeting Participants List can be found here: ", meeting_participants_sheet.url)
    

if __name__ == '__main__':
    main()

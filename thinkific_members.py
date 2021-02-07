"""
Get a list of everyone who is currently signed up as a student/member

How to use the Zoom API
1. Use the Meeting ID to get Meeting/ Webinar Info in order to get the UUID of each meeting instance
2. Use the UUID to get the specific info for each separate meeting/webinar to get the participants

Can you get specific meeting information from more than 1 UUID at a time?
How?
Ex using Goal Hack meetings
Can I create a function to get all of the instances of each weekly meeting
Create a separate function calling the first to get the participants of all the meetings?

"""
import requests
import pygsheets
import pandas as pd
import json
from google.oauth2 import service_account
import os
from datetime import datetime, date
import time
from pprint import pprint

from UnlockAcademyZTM import ua_meetings_webinars

# THINKIFIC_API_KEY = os.environ.get('THINKIFIC_API_KEY')
# THINKIFIC_SUBDOMAIN = os.environ.get('THINKIFIC_SUBDOMAIN')


# print(members_parsed["items"][1]["email"])

#   If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


with open('credentials.json') as source:
    info = json.load(source)
credentials = service_account.Credentials.from_service_account_info(info)
#   authorize Python Sheets access to Google Sheets
client = pygsheets.authorize(service_account_file='credentials.json')


ua_meetings_webinars.main()

list_of_zoom_webinar_registrants = ua_meetings_webinars.list_of_webinar_registrants
pprint(list_of_zoom_webinar_registrants)
list_of_zoom_webinar_participants = ua_meetings_webinars.list_of_webinar_participants
list_of_zoom_meeting_registrants = ua_meetings_webinars.list_of_meeting_registrants
list_of_zoom_meeting_participants = ua_meetings_webinars.list_of_meeting_participants


def main():
    
    #   Get the current time when the code starts running
    start_time = datetime.now()
    #   Get the time elapsed - current time - start time

    print("Start/Current Local Time --> " + str(time.ctime()))

    time_elapsed = datetime.now() - start_time

    get_members()
    # print(get_members())

    get_non_members()
    
    print("Store Thinkific Member Start Time --> " + str(time.ctime()))
    store_thinkific_members()
    print("Store Thinkific Members Run Time --> " + str(time_elapsed))

    store_non_members()
    print("End/Current Local Time --> " + str(time.ctime()))
    
    
members_email_name = []


def get_members():
    """
    This function will access the Thinkific API and get all of the members currently enrolled in Unlock Academy
    """
    headers = {
        'accept': 'application/json',
        'X-Auth-API-Key': os.environ.get('THINKIFIC_API_KEY'),
        'X-Auth-Subdomain': os.environ.get('THINKIFIC_SUBDOMAIN'),
    }
    # page_num = 1
    params = (
        ('page', 1),    # page_num
        # as of 9/21 there are a total of 17962 users
        # as of 11/7 there are a total of 18261 users
        ('limit', '50000')
        # ('limit', '100')
    )

    response = requests.get('https://api.thinkific.com/api/public/v1/users', headers=headers, params=params)

    members_response = response.text.encode('utf8')
    members_parsed = json.loads(members_response)
    members = members_parsed["items"]
    # next_page = members_parsed["meta"]["pagination"]["next_page"]
    # print("MEMBERS PARSED")
    # pprint(members_parsed)
    # print("NEXT PAGE IS " + str(next_page))
    # pprint(next_page)
    # Thinkific API requests are limited at 120 requests per minute.
    # run the code to check in the thinkific members but sleep for 1 minute between every 120 users
    # n = 120  # iterate over every 120th element
    # for i, x in enumerate(sample):
    #     if i % n == 0:
    #         print(i, x)
    #         time.sleep(10)
    #     else:
    #         print(i, x)
    # for i, thinkific_member_emails in enumerate(members):
    #     if i % n == 0:
    for member in members:
        # print(member)
        # member_name_split = member["name"].split(maxsplit=1)
        # if len(member_name_split) > 1:
        #     member_first_name = member_name_split[0]
        #     member_last_name = member_name_split[1]
        member = {"email": member["email"], "first_name": member["first_name"], "last_name": member["last_name"]}
        members_email_name.append(member)
        # this will result in a list of tuples [(email, name), (email, name)]
    # if next_page != "null":
    #     page_num += 1
    #     get_members(page_num)
    # pprint(members_email_name)
    # sleep for 60 secs to not reach request limit
    # time.sleep(60)
    return members_email_name


list_of_non_members = []


def get_non_members():
    """
    Function to get all student who registered and/or attended a UA Zoom Meeting/Webinars
    bub are not enrolled in Unlock Academy (not a Thinkific Member)
    Get all Meeting/Webinar Registrant/Participant data from ua_meetings_webinars.py  file
    Compare to Thinkific Members
    Return list_of_non_members
    """
    # store thinkific email addresses in a new list
    thinkific_members = members_email_name
    list_of_thinkific_member_emails = []
    for thinkific_emails in thinkific_members:
        # print("thinkific emails")
        # print(thinkific_emails["email"])
        thinkific_email = thinkific_emails["email"].lower()
        list_of_thinkific_member_emails.append(thinkific_email)
    
    # create a list just for zoom emails in order to check for duplicates later
    zoom_emails = []
    # create a list to store the zoom info for all registrants/participants in order to compare to thinkific members
    zoom_info = []
    
    for web_reg in list_of_zoom_webinar_registrants:
        web_reg_email = web_reg["email"].lower()
        
        # check if the email address in the zoom_emails list
        if web_reg_email not in zoom_emails:
            # if the email is not in the zoom_emails list, append it
            zoom_emails.append(web_reg_email)
            web_reg_first_name = web_reg["first_name"]
            
            if "last_name" in web_reg:
                web_reg_last_name = web_reg["last_name"]
                # create a dict with the user email. first name and last name (if it exists)
                web_reg_info = {"email": web_reg_email,
                                "first_name": web_reg_first_name,
                                "last_name": web_reg_last_name
                                }
                zoom_info.append(web_reg_info)
            else:
                web_reg_info = {"email": web_reg_email,
                                "first_name": web_reg_first_name
                                }
                zoom_info.append(web_reg_info)
                
    # print("Checking if WEB REG INFO is appending to ZOOM INFO")
    # pprint(zoom_info)
    
    for meet_reg in list_of_zoom_meeting_registrants:
        meet_reg_email = meet_reg["email"].lower()
        # check if the email address in the zoom_emails list
        
        if meet_reg_email not in zoom_emails:
            # if the email is not in the zoom_emails list, append it
            zoom_emails.append(meet_reg_email)
            meet_reg_first_name = meet_reg["first_name"]
            
            # create a dict with the user email. first name and last name (if it exists)
            if "last_name" in meet_reg:
                meet_reg_last_name = meet_reg["last_name"]
                meet_reg_info = {"email": meet_reg_email,
                                 "first_name": meet_reg_first_name,
                                 "last_name": meet_reg_last_name
                                 }
                zoom_info.append(meet_reg_info)
            else:
                meet_reg_info = {"email": meet_reg_email,
                                 "first_name": meet_reg_first_name
                                 }
                zoom_info.append(meet_reg_info)

    for web_participants in list_of_zoom_webinar_participants:
        web_participants_email = web_participants["email"].lower()
        
        # check if the email address in the zoom_emails list
        if web_participants_email not in zoom_emails:
            # if the email is not in the zoom_emails list, append it
            zoom_emails.append(web_participants_email)
            web_participants_first_name = web_participants["first_name"]
            
            # create a dict with the user email. first name and last name (if it exists)
            if "last_name" in web_participants:
                web_participants_last_name = web_participants["last_name"]
                web_participants_info = {"email": web_participants_email,
                                         "first_name": web_participants_first_name,
                                         "last_name": web_participants_last_name
                                         }
                zoom_info.append(web_participants_info)
            else:
                web_participants_info = {"email": web_participants_email,
                                         "first_name": web_participants_first_name
                                         }
                zoom_info.append(web_participants_info)

    for meet_participants in list_of_zoom_meeting_participants:
        meet_participants_email = meet_participants["email"].lower()
        
        # check if the email address in the zoom_emails list
        if meet_participants_email not in zoom_emails:
            # if the email is not in the zoom_emails list, append it
            zoom_emails.append(meet_participants_email)
            meet_participants_first_name = meet_participants["first_name"]
            
            # create a dict with the user email. first name and last name (if it exists)
            if "last_name" in meet_participants:
                meet_participants_last_name = meet_participants["last_name"]
                meet_participants_info = {"email": meet_participants_email,
                                          "first_name": meet_participants_first_name,
                                          "last_name": meet_participants_last_name
                                          }
                zoom_info.append(meet_participants_info)
            else:
                meet_participants_info = {"email": meet_participants_email,
                                          "first_name": meet_participants_first_name
                                          }
                zoom_info.append(meet_participants_info)
        
    # compare the zoom user info from the above to the thinkific members
    for zoom_user in zoom_info:
        # check only for email address that are not blank
        if zoom_user["email"] != "":
            email = zoom_user["email"].lower()
            
            # check if the email address from the zoom info list exists in the thinkific members emails lists
            # if it exists, they are already a member (ignore these)
            if email not in list_of_thinkific_member_emails:
                # if the email address is not in the thinkific list then create a new dict
                # and append it the list of non members
                non_member_first_name = zoom_user["first_name"]
                if "last_name" in zoom_user:
                    non_member_last_name = zoom_user["last_name"]
                    non_member_info = {"email": email,
                                       "first_name": non_member_first_name,
                                       "last_name": non_member_last_name
                                       }
                    list_of_non_members.append(non_member_info)
                else:
                    non_member_info = {"email": email,
                                       "first_name": non_member_first_name
                                       }
                    list_of_non_members.append(non_member_info)

    return list_of_non_members


def store_thinkific_members():
    """
    Function to store all Thinkific Members who are enrolled in UA in Google Sheets
    """
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    #   create a new spread sheet in the given folder
    thinkific_members_sheet = client.create(title="UA Thinkific Members " + str(report_date_time),
                                            folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    #   add a new worksheet to the spreadsheet
    thinkific_wks = thinkific_members_sheet.add_worksheet("UA Members")
    
    thinkific_df = pd.DataFrame(members_email_name)  # , columns=["Member Email Address", "Member First Name", "Member Last Name"]
    thinkific_wks.set_dataframe(thinkific_df, start=(1, 1), copy_index=False, copy_head=True, extend=True)

    # change NaN values to blanks
    thinkific_wks.replace("NaN", replacement="", matchEntireCell=True)
    
    #   format the headers in bold
    thinkific_wks.cell("A1").set_text_format("bold", True)
    thinkific_wks.cell("B1").set_text_format("bold", True)
    thinkific_wks.cell("C1").set_text_format("bold", True)

    # sort sheet by email addresses
    thinkific_wks.sort_range(start='A2', end='D50000', basecolumnindex=1, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    thinkific_members_sheet.share('', role='reader', type='anyone')
    
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Thinkific Members List can be found here: ", thinkific_members_sheet.url)


def store_non_members():
    """
    Function to store all Zoom Meeting & Webinar Registrants and Participants
    who are not non_members Members (not enrolled in UA) in Google Sheets.
    """
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    #   create a new spread sheet in the given folder
    non_members_sheet = client.create(title="UA Non Members " + str(report_date_time),
                                            folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    #   add a new worksheet to the spreadsheet
    non_members_wks = non_members_sheet.add_worksheet("Non Members")
    
    #   create headers in the worksheet (A1 and B1)
    non_members_df = pd.DataFrame(list_of_non_members)  # , columns=["Member Email Address", "Member First Name", "Member Last Name"]
    
    non_members_wks.set_dataframe(non_members_df, start=(1, 1), copy_index=False, copy_head=True, extend=True)

    # change NaN values to blanks
    non_members_wks.replace("NaN", replacement="", matchEntireCell=True)
    
    #   format the headers in bold
    non_members_wks.cell("A1").set_text_format("bold", True)
    non_members_wks.cell("B1").set_text_format("bold", True)
    non_members_wks.cell("C1").set_text_format("bold", True)

    # sort sheet by email addresses
    non_members_wks.sort_range(start='A2', end='D50000', basecolumnindex=1, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    non_members_sheet.share('', role='reader', type='anyone')
    
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The Non Members List can be found here: ", non_members_sheet.url)
    
    
"""
Run the code to get thinkific members
check if members already exist in the sheet
    use find() function for pygsheets
if a user does not exist in the sheet, store them in the new member dict
append the new member dict to the end of the sheet
"""


if __name__ == '__main__':
    main()

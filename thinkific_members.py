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
# from __future__ import print_function
import pygsheets
import pandas as pd
import json
from google.oauth2 import service_account
import os
from datetime import datetime
import time

#   Get the current time when the code starts running
start_time = datetime.now()
#   Get the time elapsed - current time - start time

print("Start/Current Local Time --> " + str(time.ctime()))

# THINKIFIC_API_KEY = os.environ.get('THINKIFIC_API_KEY')
# THINKIFIC_SUBDOMAIN = os.environ.get('THINKIFIC_SUBDOMAIN')

headers = {
    'accept': 'application/json',
    'X-Auth-API-Key': os.environ.get('THINKIFIC_API_KEY'),
    'X-Auth-Subdomain': os.environ.get('THINKIFIC_SUBDOMAIN'),
}


params = (
    ('page', '1'),
    # as of 9/21 there are a total of 17962 users
    ('limit', '20000')
    # ('limit', '500')
)

response = requests.get('https://api.thinkific.com/api/public/v1/users', headers=headers, params=params)

members_response = response.text.encode('utf8')
members_parsed = json.loads(members_response)

# print(members_parsed["items"][1]["email"])

#   If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


with open('credentials.json') as source:
    info = json.load(source)
credentials = service_account.Credentials.from_service_account_info(info)
#   authorize Python Sheets access to Google Sheets
client = pygsheets.authorize(service_account_file='credentials.json')


def main():
    # print(THINKIFIC_SUBDOMAIN)
    get_members()
    # print(get_members())
    store_thinkific_members()


def get_members():
    """
    This function will access the Thinkific API and get all of the members currently enrolled in Unlock Academy
    """
    members = members_parsed["items"]
    members_email_name = []
    for member in members:
        member = member["email"], member["full_name"]
        members_email_name.append(member)
        # this will result in a list of tuples [(email, name), (email, name)]
        # sort by email addresses of tuple which is the 1st element of each tuple
        members_email_name.sort(key=lambda tup: tup[1])
    return members_email_name


# get_members()
# print(get_members())


def store_thinkific_members():
    """
    Function to store all Thinkific Members who are enrolled in UA in Google Sheets
    """
    # authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')

    #   create a new spread sheet in the given folder
    thinkific_members_sheet = client.create(title="UA Thinkific Members", folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    #   add a new worksheet to the spreadsheet
    thinkific_wks = thinkific_members_sheet.add_worksheet("Members")
    #   create headers in the worksheet (A1 and B1)
    # thinkific_wks.insert_rows(0, values=["Member Email Address", "Member Name"])
    thinkific_df = pd.DataFrame(get_members(), columns=["Member Email Address", "Member Name"])
    thinkific_wks.set_dataframe(thinkific_df, start=(1, 1), copy_index=False, copy_head=True)
    # thinkific_object = thinkific_df.select_dtypes(['object'])
    # thinkific_df[thinkific_object.columns] = thinkific_object.apply(lambda x: x.str.strip())
    thinkific_df["Member Name"] = thinkific_df["Member Name"].str.strip()
    #   format the headers in bold
    thinkific_wks.cell("A1").set_text_format("bold", True)
    thinkific_wks.cell("B1").set_text_format("bold", True)
#     #   run the get_members function from the thinkific_members.py file and store them in the ua_members variable
#     ua_members = get_members()
#     #   loop through all of the members and get the email address (index 0) and the name (index 1)
#     for member in ua_members:
#         member_email = member[0]
#         member_name = member[1]
#         #   insert a new row for each member starting on row 1. Column A = email addresses, Column B = Name
#         thinkific_wks.insert_rows(1, values=[member_email, member_name])
#     #   TODO: figure out if I can just make the end of the sort the last field in column B.
#     #       if the above is not possible, get the last field through code (since this will change),
#     #       then insert variable it below
#     #   Sort the spreadsheet by the members names
#         if member[1] is 'unlock student':
#     thinkific_wks.sort_range(start='A2', end='B20000', basecolumnindex=1, sortorder='ASCENDING')
    thinkific_df.sort_values(by=['Member Name', 'Member Email Address'])
    #   Share spreadsheet with read only access to anyone with the link
    thinkific_members_sheet.share('', role='reader', type='anyone')
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Thinkific Members List can be found here: ", thinkific_members_sheet.url)
    print("End/Current Local Time --> " + str(time.ctime()))
    time_elapsed = datetime.now() - start_time
    print("Thinkific Members Run Time --> " + str(time_elapsed))


"""
Run the code to get thinkific members
check if members already exist in the sheet
    use find() function for pygsheets
if a user does not exist in the sheet, store them in the new member dict
append the new member dict to the end of the sheet
"""
# if members_parsed["email"] not in thinkific_members_sheet:
#     new_member = []
#     new_member.append()


if __name__ == '__main__':
    main()

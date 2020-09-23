"""
Access Google Sheets API
Print data from Sheet
Update data within sheet
Google Sheet URL:
    https://docs.google.com/spreadsheets/d/1-s_PJxHErxVFiIYE9Ml_mq6eAS16nFUtuyr2xZ3nnRc/edit#gid=0
References:
    https://pygsheets.readthedocs.io/en/master/index.html
    https://sempioneer.com/python-for-seo/google-sheets-with-python/
    https://medium.com/swlh/how-i-automate-my-church-organisations-zoom-meeting-attendance-reporting-with-python-419dfe7da58c
"""
from __future__ import print_function
import pygsheets
import pandas as pd
import json
from google.oauth2 import service_account
from pprint import pprint
from aug23_goalhack import get_students, get_all_goalhack_participants


"""
Data Flow
1. Access Zoom API to get meeting/webinar participants - done
2. Pull Data from Zoom and store email : name key/value pairs in Google Sheet - done
3. Access Thinkific API to get current students/members
4. Pull Data from Thinkific and store email : name key/value pairs in separate Google Sheet
5. Compare the Zoom list to Thinkific list
    If someone is in both lists - they are a already student/member - ignore these people - will be deleted from Zoom list
    If someone is in Zoom list but NOT Thinkific - they are not yet a student/member - want to email these people
        Should I keep the original Zoom List and just create a new list to push to MailChimp??
            Is there reason to keep the list with all Zoom meeting/webinar participants before removing members
6. Access MailChimp API to email people who are not yet members (in Zoom list ONLY)
7. Push email : name key/value pairs to MailChimp (this will just be the edited Zoom list with the members removed) 
Automate the report so that it can be run every week
"""

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1-s_PJxHErxVFiIYE9Ml_mq6eAS16nFUtuyr2xZ3nnRc'
RANGE_NAME = 'A:B'

with open('credentials.json') as source:
    info = json.load(source)
credentials = service_account.Credentials.from_service_account_info(info)
# client = pygsheets.authorize(service_account_file='credentials.json')


def main():

    # authorize Python Sheets access to Google Sheets
    client = pygsheets.authorize(service_account_file='credentials.json')

    # access Google Sheet by the sheet ID
    sheet = client.open_by_key('1-s_PJxHErxVFiIYE9Ml_mq6eAS16nFUtuyr2xZ3nnRc')

    # access the specific sheet within the spreadsheet
    worksheet = sheet.worksheet_by_title('Sheet1')

    # get specific cell range
    cell_range = worksheet.range('A:B', returnas='matrix')

    # sort the worksheet by Name Column in Ascending order
    sorted_worksheet = worksheet.sort_range(start='A2', end='B6', basecolumnindex=0, sortorder='ASCENDING')

    # run the function from aug23_goalhack to get all the student information
    student_email_name = get_students()

    # insert a new row with given values
    for student in student_email_name:
        email = student[0]
        name = student[1]
        new_row = worksheet.insert_rows(1, values=[email, name])

    # get all values currently in the spreadsheet
    all_values = worksheet.get_all_values(majdim='ROWS', include_tailing_empty=False)

    cleaned_values = [[item for item in row if item]for row in all_values]
    # [[item for item in unique_list if item]for unique_list in all_values]

    # print(all_values)

    """
    Use a try/except
    Check if a sheet named "Trading Bot Participants" already exists
    If it exists 
        add the email addresses and names in that sheet
    If it does not exist
        create a new sheet named "Trading Bot Participants
        then add the email addresses and names in that sheet
    """
    # # Create a new sheet in the UA Zoom Folder names GoalHack Participants
    # new_sheet = client.create(title="GoalHack Participants", folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    # new_worksheet = new_sheet.add_worksheet(title="Aug-30-20", cols=2)


# TODO: Edit to get dictionary from get_students() function in aug23_goalhack.py
"""
Below - Code for later to use to compare Zoom List to Thinkific List
    currently using test data for functionality
"""

# def flip_dictionary(a_dict):
#     new_dict = {}
#     for k, v in a_dict.items():
#         new_dict.update({k.lower(): v})
#     return new_dict


# def get_participants():
#     # dict1 to represent Zoom
#     attended_zoom = {
#         'amanda.green@gmail.com': 'Amanda Green',
#         'chris.jackson@gmail.com': 'Chris Jackson',
#         'danae.winston@gmail.com': "Danae' Winston",
#         'sam.richardson@gmail.com': 'Sam Richardson',
#         'TONYA.FRANSHAW@GMAIL.COM': 'Tonya Franshaw',
#         'tricy2008@yahoo.com': "Mon'Trice Brightmon",
#         'Matthew.richardson@gmail.com': 'Matthew Richardson',
#         'taras.winston@gmail.com': 'Taras Winston'
#     }
#     # dict2 to represent members from Thinkific
#     already_member = {'brian.jones@gmail.com': 'Brian Jones',
#                       'chris.jackson@gmail.com': 'CHRIS JACKSON',
#                       'gabrielle.brightmon@gmail.com': 'Gabrielle Brightmon',
#                       'james.davis@gmail.com': 'James Davis',
#                       'sam.richardson@gmail.com': 'Sam Richardson',
#                       'TRICY2008@YAHOO.COM': "MON'TRICE BRIGHTMON"
#                       }
#
#     attended_zoom_flipped = flip_dictionary(attended_zoom)
#     already_member_flipped = flip_dictionary(already_member)
#     # pprint(attended_zoom_flipped)
#     # pprint(already_member_flipped)
#     # not_emailed_lower = attended_zoom.lower()
#     # already_emailed_lower = already_member.lower()
#     should_email = {}
#     for email, name in attended_zoom_flipped.items():
#         if email.lower() not in already_member_flipped:
#             should_email.update({email.lower(): name})
#     return should_email
#     # email address and names left in should_email will be stored in the list for MailChimp


"""
How to use the Zoom API
1. Use the Meeting ID to get Meeting/ Webinar Info in order to get the UUID of each meeting instance
2. Use the UUID to get the specific info for each separate meeting/webinar to get the participants

Can you get specific meeting information from more than 1 UUID at a time?
How?
Ex using Goal Hack meetings
Can I create a function to get all of the instances of each weekly meeting
Create a separate function calling the first to get the participants of all the meetings?
"""

# TODO: How to automate report??
"""
For Loop to get all of the meetings
Store each meeting in a variable?
For loop to go through the meeting to get the participants
"""

if __name__ == '__main__':
    main()

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
import aug23_goalhack


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

with open('zoom_student_info.json') as source:
    student_info = json.load(source)
print(type(student_info))


for email, name in student_info:
    email = student_info
    name = student_info
    print(email, name)


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

    # insert a new row with given values
    # TODO: Need help here to get email and name key/values from dictionary in json file
    # need to figure out why each student is a dictionary and how to parse through it
    new_row = worksheet.insert_rows(1, values=[student_info[0], student_info[1]])

    # get all values currently in the spreadsheet
    all_values = worksheet.get_all_values(majdim='ROWS', include_tailing_empty=False)

    cleaned_values = [[item for item in row if item]for row in all_values]
    # [[item for item in unique_list if item]for unique_list in all_values]

    # print(all_values)

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


# TODO: How to automate report??
"""
For Loop to get all of the meetings
Store each meeting in a variable?
For loop to go through the meeting to get the participants
"""

if __name__ == '__main__':
    main()

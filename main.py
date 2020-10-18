"""
This goal of this program is to access and pull data from the Zoom, Thinkific, MailChimp and Google Sheets APIs
1. Access the Zoom API to get the participants from Unlock Academy Webinars
2. Access the Thinkific API to get the current Students/Member enrolled in Unlock Academy
3. Compare the participants who attended webinars to the members enrolled in UA
4. Access the MailChimp API to push a new email list for the webinar registrants that are not yet enrolled in UA
5. Access Google Sheets API to store the Email Addresses and Names gathered from each of the above APIs
6. Schedule the job to run at a set interval to check for new members and run the compare again then update MailChimp

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
from datetime import datetime
import time
import schedule
from pprint import pprint
from UnlockAcademyZTM.aug23_goalhack import get_students
from UnlockAcademyZTM import ua_trading_bot_webinar, thinkific_members


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

#   Get the current time when the code starts running
start_time = datetime.now()
#   Get the time elapsed - current time - start time
time_elapsed = datetime.now() - start_time
print("Start/Current Local Time --> " + str(time.ctime()))


#   If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


with open('credentials.json') as source:
    info = json.load(source)
credentials = service_account.Credentials.from_service_account_info(info)
#   authorize Python Sheets access to Google Sheets
client = pygsheets.authorize(service_account_file='credentials.json')


def main():

    #   authorize Python Sheets access to Google Sheets
    # client = pygsheets.authorize(service_account_file='credentials.json')

    participants_not_members()

    #   10/10 started at 4:04am
    print("Total Time --> " + str(time_elapsed) + " Current Local Time --> " + str(time.ctime()))


"""
Use a try/except
Check if a sheet named "UA Thinkific Members" already exists
If it exists 
    add the email addresses and names in that sheet
If it does not exist
    create a new sheet named "UA Thinkific Members"
    then add the email addresses and names in that sheet
"""


def check_new_members():
    thinkific_members_sheet = client.open(title="UA Thinkific Members")
    thinkific_wks = thinkific_members_sheet.worksheet_by_title("Members")
    #   if the Spread Sheet and Worksheet exist run the function to get all the members
    ua_members = thinkific_members.get_members()
    for member in ua_members:
        member_email = member[0]
        member_name = member[1]
        thinkific_wks.insert_rows(1, values=[member_email, member_name])


def flip_dictionary(a_dict):
    """
    Function to flip the lists to email : name instead of name : email order
    """
    new_dict = {}
    for k, v in a_dict.items():
        new_dict.update({k.lower(): v})
    return new_dict


def participants_not_members():
    """
    Function to compare the webinar participants to the current members
    Return only participants who attended the webinar but are NOT yet signed up as members
    """
    #   dict to represent Zoom webinar registrants
    webinar_participants = {}
    webinar_participants.update(ua_trading_bot_webinar.get_tbot_students())
    #   dict to represent members from Thinkific
    already_ua_student = {}
    already_ua_student.update(thinkific_members.get_members())

    webinar_participants_flipped = flip_dictionary(webinar_participants)
    already_ua_student_flipped = flip_dictionary(already_ua_student)
    # pprint(attended_zoom_flipped)
    # pprint(already_member_flipped)
    should_email = {}
    #   loop through Zoom participants dict
    for email, name in webinar_participants_flipped.items():
        #   if a Zoom participant is not in the Thinkific Member list add them to the should_email dict
        if email not in already_ua_student_flipped:
            should_email.update({email.lower(): name})
    #   email address and names left in should_email will be stored in the list for MailChimp

    # client = pygsheets.authorize(service_account_file='credentials.json')
    mailchimp_email_list = client.create(title="MailChimp Email List", folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    mailchimp_wks = mailchimp_email_list.add_worksheet("MailChimp Email List")
    # mailchimp_wks.adjust_column_width(start=0, end=1, pixel_size=300)
    mailchimp_wks.insert_rows(0, values=["Member Email Address", "Member Name"])
    mailchimp_wks.cell("A1").set_text_format("bold", True)
    mailchimp_wks.cell("B1").set_text_format("bold", True)
    for mailchimp_contact in should_email:
        mailchimp_contact_email = mailchimp_contact[0]
        mailchimp_contact_name = mailchimp_contact[1]
        mailchimp_wks.insert_rows(1, values=[mailchimp_contact_email, mailchimp_contact_name])

    mailchimp_wks.sort_range(start='A2', end='B100', basecolumnindex=1, sortorder='ASCENDING')
    # Share spreadsheet with read only access
    mailchimp_email_list.share('', role='reader', type='anyone')
    print("The UA MailChimp List can be found here: ", mailchimp_email_list.url)

    print("Comparison Run Time --> " + str(time.time() - start_time))


#   TODO:
#    schedule job using Windows Task Scheduler instead (Cron job in Mac/Linux)
#    or PythonAnywhere or AWS
    # schedule.every().sunday.at("0:00").do(participants_not_members())
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

"""
use Python schedule module to automate the report
resource --> https://schedule.readthedocs.io/en/stable/
"""

if __name__ == '__main__':
    main()

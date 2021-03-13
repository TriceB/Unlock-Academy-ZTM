"""
Import main() function and lists from ua_meetings_webinars.py
to get data about meetings/webinars registrants/participants

Access Thinkific API to get all courses, students, and student enrollments.

Compare Zoom registrants/participants to Thinkific Members and return all non-members

Store courses, students, enrollments, and non-members to Google Sheets
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
from pygsheets.datarange import DataRange
import ua_meetings_webinars

# THINKIFIC_API_KEY = os.environ.get('THINKIFIC_API_KEY')
# THINKIFIC_SUBDOMAIN = os.environ.get('THINKIFIC_SUBDOMAIN')


# print(members_parsed["items"][1]["email"])

#   If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']

script_directory = os.path.dirname(os.path.abspath(__file__))
credentials_file = os.path.join(script_directory, 'credentials.json')
with open(credentials_file) as source:
    info = json.load(source)
credentials = service_account.Credentials.from_service_account_info(info)
#   authorize Python Sheets access to Google Sheets
client = pygsheets.authorize(service_account_file=credentials_file)


ua_meetings_webinars.main()

list_of_zoom_webinar_registrants = ua_meetings_webinars.list_of_webinar_registrants
# pprint(list_of_zoom_webinar_registrants)
list_of_zoom_webinar_participants = ua_meetings_webinars.list_of_webinar_participants
list_of_zoom_meeting_registrants = ua_meetings_webinars.list_of_meeting_registrants
list_of_zoom_meeting_participants = ua_meetings_webinars.list_of_meeting_participants

headers = {
        'accept': 'application/json',
        'X-Auth-API-Key': os.environ.get('THINKIFIC_API_KEY'),
        'X-Auth-Subdomain': os.environ.get('THINKIFIC_SUBDOMAIN')
}


def main():
    
    #   Get the current time when the code starts running
    start_date_time = datetime.now()
    #   Get the time elapsed - current time - start time

    start_time = time.perf_counter()
    print("Start thinkific_members.py /Current Local Time --> " + str(time.ctime()) + " Perf counter " + str(time.perf_counter()))

    time_elapsed = datetime.now() - start_date_time
    
    get_thinkific_courses()
    # pprint(list_thinkific_courses)
    courses_timer = time.perf_counter()
    print("Get Thinkific Courses Run Time --> " + str(courses_timer))
    
    get_members()
    # pprint(list_of_members)
    get_members_timer = time.perf_counter() - start_time
    print("Members Run Time --> " + str(get_members_timer))
    
    get_student_enrollments()
    # pprint(list_of_student_enrollments)
    enrollments_timer = time.perf_counter() - start_time
    print("Enrollments Run Time --> " + str(enrollments_timer))
    
    get_non_members()
    non_members_timer = time.perf_counter() - start_time
    print("Non Members Run Time --> " + str(non_members_timer))
    
    store_thinkific_courses()
    store_courses_timer = time.perf_counter() - start_time
    print("Store Thinkific Member Start Time --> " + str(store_courses_timer))

    store_thinkific_members()
    store_members_timer = time.perf_counter() - start_time
    print("Store Thinkific Members Run Time --> " + str(store_members_timer))

    store_student_enrollments()
    store_enrollments_timer = time.perf_counter() - start_time
    print("Store Enrollments Run Time --> " + str(store_enrollments_timer))

    store_non_members()
    store_non_members_timer = time.perf_counter() - start_time
    print("Store Non Members Run Time --> " + str(store_non_members_timer))

    print("End/Current Local Time --> " + str(time.ctime()))


list_thinkific_courses = []


def get_thinkific_courses(page_num=1):
    params = (
        ('page', page_num),  # page_num
        # ('limit', '50000')
        # ('limit', '200')
    )
    response = requests.get('https://api.thinkific.com/api/public/v1/courses?', headers=headers, params=params)
    courses_response = response.text.encode('utf8')
    courses_parsed = json.loads(courses_response)
    courses = courses_parsed["items"]
    current_page = courses_parsed["meta"]["pagination"]["current_page"]
    # print("CURRENT PAGE = ", current_page)
    next_page = courses_parsed["meta"]["pagination"]["next_page"]
    # print("NEXT PAGE = ", next_page)
    total_pages = courses_parsed["meta"]["pagination"]["total_pages"]
    total_items = courses_parsed["meta"]["pagination"]["total_items"]
    # print("TOTAL ITEMS = ", total_items)
    # print("TOTAL PAGES = ", total_pages)
    
    for course in courses:
        course_info = {"course_name": course["name"],
                       "course_id": course["id"],
                       "course_instructor": course["instructor_id"]
                       }
        list_thinkific_courses.append(course_info)
        
    if current_page != total_pages:
        page_num += 1
        get_thinkific_courses(page_num)
    else:
        print("The End of get_thinkific_courses")
    return list_thinkific_courses

    
list_of_members = []


def get_members(page_num=1):  # page_num=1
    """
    This function will access the Thinkific API and get all of the members currently enrolled in Unlock Academy
    """
    # page_num = 1
    params = (
        ('page', page_num),  # page_num
        # as of 9/21 there are a total of 17962 users
        # as of 11/7 there are a total of 18261 users
        ('limit', '1000')
        # ('limit', '100')
    )
    
    response = requests.get('https://api.thinkific.com/api/public/v1/users', headers=headers, params=params)
    members_response = response.text.encode('utf8')
    members_parsed = json.loads(members_response)
    members = members_parsed["items"]
    # pprint(members_parsed)
    current_page = members_parsed["meta"]["pagination"]["current_page"]
    # print("CURRENT PAGE = ", current_page)
    next_page = members_parsed["meta"]["pagination"]["next_page"]
    # print("NEXT PAGE = ", next_page)
    total_pages = members_parsed["meta"]["pagination"]["total_pages"]
    total_items = members_parsed["meta"]["pagination"]["total_items"]
    # print("TOTAL ITEMS = ", total_items)
    # print("TOTAL PAGES = ", total_pages)
    # print("MEMBERS PARSED")
    # pprint(members_parsed)
    # print("NEXT PAGE IS " + str(next_page))
    # pprint(next_page)
    # Thinkific API requests are limited at 120 requests per minute.
    # run the code to check in the thinkific members but sleep for 1 minute between every 120 users
    # n = 120  # iterate over every 120th element
    # for i, x in enumerate(members):
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
        member = {"email": member["email"],
                  "first_name": member["first_name"],
                  "last_name": member["last_name"],
                  "student_id": member["id"]
                  }
        list_of_members.append(member)
        
    if current_page != total_pages:
        page_num += 1
        get_members(page_num)
    else:
        print("The End of get_members()")
    # pprint(list_of_members)
    # sleep for 60 secs to not reach request limit
    # time.sleep(60)
    return list_of_members


list_of_student_enrollments = []


def get_student_enrollments(page_num=1):  # page_num=1
    """
    Function to get all Students and the classes they are enrolled in
    """
    
    # page_num = 1
    params = (
        ('page', page_num),  # page_num
        # ('limit', '50000')
        ('limit', '1000')
    )
    response = requests.get('https://api.thinkific.com/api/public/v1/enrollments?', headers=headers, params=params)
    students_response = response.text.encode('utf8')
    students_parsed = json.loads(students_response)
    students = students_parsed["items"]
    current_page = students_parsed["meta"]["pagination"]["current_page"]
    # print("CURRENT PAGE = ", current_page)
    next_page = students_parsed["meta"]["pagination"]["next_page"]
    # print("NEXT PAGE = ", next_page)
    total_pages = students_parsed["meta"]["pagination"]["total_pages"]
    total_items = students_parsed["meta"]["pagination"]["total_items"]
    # print("TOTAL ITEMS = ", total_items)
    # print("TOTAL PAGES = ", total_pages)
    
    for student in students:
        student_email = student["user_email"].lower()
        student_name_split = student["user_name"].split(maxsplit=1)
        
        course_start_date = student["started_at"]
        course_completion_date = student["completed_at"]
        # print("Course Start Date - ", course_start_date, "Completion Date - ", course_completion_date)
        
        if isinstance(course_start_date, str):
            start_date_format = '%Y-%m-%dT%H:%M:%S.%f%z'
            course_start_date = datetime.strptime(course_start_date, start_date_format)
            # print("Course Start Date - ", course_start_date)
        
        if isinstance(course_completion_date, str):
            completion_date_format = '%Y-%m-%dT%H:%M:%S.%f%z'
            course_completion_date = datetime.strptime(course_completion_date, completion_date_format)
            # print("Completion Date - ", course_completion_date)
            
        if len(student_name_split) > 1:
            student_first_name = student_name_split[0]
            student_last_name = student_name_split[1]
            student_info = {"email": student_email,
                            "first_name": student_first_name,
                            "last_name": student_last_name,
                            "course_name": student["course_name"],
                            "course_id": student["course_id"],
                            "course_started": course_start_date,
                            "completion_status": student["completed"],
                            "percentage_completed": student["percentage_completed"],
                            "date_completed": course_completion_date
                            }
            list_of_student_enrollments.append(student_info)
        else:
            student_first_name = student_name_split[0]
            student_info = {"email": student_email,
                            "first_name": student_first_name,
                            "course_name": student["course_name"],
                            "course_id": student["course_id"],
                            "course_started": course_start_date,
                            "completion_status": student["complete"],
                            "percentage_completed": student["percentage_completed"],
                            "date_completed": course_completion_date
                            }
            list_of_student_enrollments.append(student_info)
    
    if current_page != total_pages:
        page_num += 1
        get_student_enrollments(page_num)
    
    else:
        print("The End of get_student_enrollments()")
        
    return list_of_student_enrollments
    
    
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
    thinkific_members = list_of_members
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


def store_thinkific_courses():
    """
    Function to store all Thinkific Courses in UA in Google Sheets
    """
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    #   create a new spread sheet in the given folder
    thinkific_courses_sheet = client.create(title="UA Thinkific Courses " + str(report_date_time),
                                            folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    #   add a new worksheet to the spreadsheet
    thinkific_courses_wks = thinkific_courses_sheet.add_worksheet("UA Courses")
    
    thinkific_courses_df = pd.DataFrame(list_thinkific_courses)
    thinkific_courses_wks.set_dataframe(thinkific_courses_df, start=(1, 1), copy_index=False, copy_head=True,
                                        extend=True)
    
    # change NaN values to blanks
    thinkific_courses_wks.replace("NaN", replacement="", matchEntireCell=True)
    
    #   format the headers in bold
    thinkific_courses_wks.cell("A1").set_text_format("bold", True)
    thinkific_courses_wks.cell("B1").set_text_format("bold", True)
    thinkific_courses_wks.cell("C1").set_text_format("bold", True)
    
    # sort sheet by email addresses
    thinkific_courses_wks.sort_range(start='A2', end='D50000', basecolumnindex=0, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    thinkific_courses_sheet.share('', role='reader', type='anyone')
    
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Thinkific Courses List can be found here: ", thinkific_courses_sheet.url)


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
    
    thinkific_df = pd.DataFrame(list_of_members)  # , columns=["Member Email Address", "Member First Name", "Member Last Name"]
    thinkific_wks.set_dataframe(thinkific_df, start=(1, 1), copy_index=False, copy_head=True, extend=True)

    # change NaN values to blanks
    thinkific_wks.replace("NaN", replacement="", matchEntireCell=True)
    
    #   format the headers in bold
    # thinkific_wks.cell("A1").set_text_format("bold", True)
    # thinkific_wks.cell("B1").set_text_format("bold", True)
    # thinkific_wks.cell("C1").set_text_format("bold", True)
    
    bold_cell = thinkific_wks.cell('A1')
    bold_cell.set_text_format('bold', True)
    DataRange('A1', 'L1', worksheet=thinkific_wks).apply_format(bold_cell)

    # sort sheet by email addresses
    thinkific_wks.sort_range(start='A2', end='L50000', basecolumnindex=1, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    thinkific_members_sheet.share('', role='reader', type='anyone')
    
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Thinkific Members List can be found here: ", thinkific_members_sheet.url)


def store_student_enrollments():
    """
        Function to store all Student Enrollments in UA in Google Sheets
        """
    today_date_time = datetime.now()
    report_date_time = today_date_time.strftime("%b %d, %Y %H:%M:%S")
    #   create a new spread sheet in the given folder
    student_enrollments_sheet = client.create(title="UA Student Enrollments " + str(report_date_time),
                                              folder="1cIjZbTLwNEDo4YdknD8bUu9VPx-Ky7I-")
    
    #   add a new worksheet to the spreadsheet
    student_enrollments_wks = student_enrollments_sheet.add_worksheet("UA Student Enrollments")
    
    student_enrollments_df = pd.DataFrame(list_of_student_enrollments)
    student_enrollments_wks.set_dataframe(student_enrollments_df, start=(1, 1), copy_index=False, copy_head=True,
                                          extend=True)
    
    #   format the headers in bold
    # student_enrollments_wks.cell("A1").set_text_format("bold", True)
    # student_enrollments_wks.cell("B1").set_text_format("bold", True)
    # student_enrollments_wks.cell("C1").set_text_format("bold", True)
    # student_enrollments_wks.cell("D1").set_text_format("bold", True)
    # student_enrollments_wks.cell("E1").set_text_format("bold", True)
    # student_enrollments_wks.cell("F1").set_text_format("bold", True)
    # student_enrollments_wks.cell("G1").set_text_format("bold", True)
    # student_enrollments_wks.cell("H1").set_text_format("bold", True)
    # student_enrollments_wks.cell("I1").set_text_format("bold", True)

    bold_cell = student_enrollments_wks.cell('A1')
    bold_cell.set_text_format('bold', True)
    DataRange('A1', 'L1', worksheet=student_enrollments_wks).apply_format(bold_cell)
   
    # change NaN values to blanks
    student_enrollments_wks.replace("NaN", replacement="", matchEntireCell=True)

    # sort sheet by email addresses
    student_enrollments_wks.sort_range(start='A2', end='L50000', basecolumnindex=0, sortorder='ASCENDING')
    
    #   Share spreadsheet with read only access to anyone with the link
    student_enrollments_sheet.share('', role='reader', type='anyone')
    
    #   print the direct link to the spreadsheet for the user running the code to access
    print("The UA Student Enrollments List can be found here: ", student_enrollments_sheet.url)


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

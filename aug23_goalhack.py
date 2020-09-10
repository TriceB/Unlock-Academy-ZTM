import json

import requests
from ua_goalhack_meetings import get_meetings

# TODO: Find a way to parse through the URL and use a for loop to go through and insert a new meeting UUID each time
# UUID will go in between "past_meetings/" and "participants"
# "https://api.zoom.us/v2/past_meetings/{ZOOM_UUID}/participants?page_size=30&next_page_token="
url = "https://api.zoom.us/v2/past_meetings/2K/5jZWeSRK+PYNeT2Y/7A==/participants?page_size=30&next_page_token="

payload = {}
headers = {
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIaFZmRTRaTVNZTzloRUpGMkttenVRIiwiZXhwIjoxNjA2MTA0MjM5fQ.DnWPwA3qIvqdRUmVmSfyCA8G_I3rcLJkOXohKkUF2Rw',
  'Cookie': '_zm_lang=en-US; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_date_format=mm/dd/yy; cred=162E1B2635A5EB3E99DF48411DA1B37B'
}

response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text.encode('utf8'))
zoom_data = response.text.encode('utf8')

parsed_response = json.loads(zoom_data)
# print(parsed_response)


def get_students():
    participants = parsed_response["participants"]
    student_email_name = []
    for students in participants:
        student = students["user_email"], students["name"]
        student_email_name.append(student)
    return student_email_name


get_students()
# print(get_students())
"""
Old Code
    for students in participants:
        # name = students["name"]
        # email = students["user_email"]
        # student_data = {"email ": email, "name ": name}
        # student_email_name.append(student_data)
        # print(students["user_email"] + " : " + students["name"])
        student = students["user_email"], students["name"]
        return students["user_email"] + " : " + students["name"]
Note:
return students["user_email"] + " : " + students["name"]
vs
print(students["user_email"] + " : " + students["name"])

return statement would not work even though the same thing in a print statement will print everything
why?
because the return statement causes the loop to stop after the first run so it will only return the first name
print works because it does not stop the loop. 
this was solved by creating an empty list and appending the new values to the list each time the loop runs 
then returning the list
"""


# TODO: work on the below code for parsing through the URL
# ZOOM_UUID = get_meetings()
# print(ZOOM_UUID)
#
# for goalhack_UUID in ZOOM_UUID:
#     first_half = url.split("past_meetings/")
#     second_half = first_half[1:][0].split("/participants?")[0]
#     # second_half = ZOOM_UUID
#     print(second_half)
#
# import urllib
# from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit, urlparse, urljoin
#
# meeting_url = "https://api.zoom.us/v2/past_meetings/2K/5jZWeSRK+PYNeT2Y/7A==/participants?page_size=30&next_page_token="
# parsed_url = urlparse(meeting_url)
# print(parsed_url)


'''
parsed url
ParseResult(
scheme='https', 
netloc='api.zoom.us', 
path='/v2/past_meetings/2K/5jZWeSRK+PYNeT2Y/7A==/participants', 
params='', query='page_size=30&next_page_token=', 
fragment='')
'''
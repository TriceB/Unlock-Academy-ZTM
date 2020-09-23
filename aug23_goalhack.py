import json
from urllib.parse import urljoin
import requests
from ua_goalhack_meetings import get_meetings

# TODO: Find a way to parse through the URL and use a for loop to go through and insert a new meeting UUID each time
# UUID will go in between "past_meetings/" and "participants"
# "https://api.zoom.us/v2/past_meetings/{ZOOM_UUID}/participants?page_size=30&next_page_token="

'''
parsed url
ParseResult(
scheme='https', 
netloc='api.zoom.us', 
path='/v2/past_meetings/2K/5jZWeSRK+PYNeT2Y/7A==/participants', 
params='', query='page_size=30&next_page_token=', 
fragment='')
'''

# run the function to get all the meeting uuids for each Goal Hack Meeting
uuids = get_meetings()


# function to use the uuids from above and use them to create a new url for each uuid
def get_urls():
    new_url_with_uuid = []
    for ids in uuids:
        meeting_scheme_net = "https://api.zoom.us"
        meeting_path = '/v2/past_meetings/' + str(ids) + '/participants?page_size=30&next_page_token='
        meeting_url_joined = urljoin(meeting_scheme_net, meeting_path)
        new_url_with_uuid.append(meeting_url_joined)
    return new_url_with_uuid


get_urls()
# print(get_urls())

# this will call the function to get the urls created above
url = str(get_urls())

payload = {}
headers = {
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIaFZmRTRaTVNZTzloRUpGMkttenVRIiwiZXhwIjoxNjA2MTA0MjM5fQ.DnWPwA3qIvqdRUmVmSfyCA8G_I3rcLJkOXohKkUF2Rw',
  'Cookie': '_zm_lang=en-US; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_date_format=mm/dd/yy; cred=162E1B2635A5EB3E99DF48411DA1B37B'
}


# function to get the email and name who attended for each meeting
def get_students():
    participants = parsed_response["participants"]
    student_email_name = []
    for students in participants:
        student = students["user_email"], students["name"]
        student_email_name.append(student)
        student_email_name.sort(key=lambda tup: tup[1])
    return student_email_name


# for each url created above, parse through the url then run the function to get the students
for urls in get_urls():
    response = requests.request("GET", urls, headers=headers, data=payload)
    # print(response.text.encode('utf8'))
    zoom_data = response.text.encode('utf8')
    parsed_response = json.loads(zoom_data)
    # print(parsed_response)
    get_students()
    print(get_students())


# get_students()
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

'''
How should I handle the duplicates for 1 meeting?
How should I handle the duplicates across all of the meetings?
Each set of participants is [List] of (Tuples) - [(email, name), (email, name)]
Options
1. 1a. Go through each meeting list separately and remove duplicates 
    1b. then create one large list of tuples (this would be 1 list of all participants across all meetings)
            this would still have duplicates because people have attended multiple meetings
    1c. then remove duplicates from the larger list 
2. 2a. Take each list and append them to one another creating the large list of tuples
    2b. go through the large list and remove duplicates 
    Is there any reason to keep the participants from each separate?
'''
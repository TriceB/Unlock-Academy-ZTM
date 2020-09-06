import requests
import json

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
    for students in participants:
        name = students["name"]
        email = students["user_email"]
        student_data = {"email ": email, "name ": name}
        student_email_name.append(student_data)


student_email_name = []
get_students()

with open('zoom_student_info.json', 'w') as file:
    json.dump(student_email_name, file)

# for name, email in students:
#     name = students["name"]
#     # print(name)


# for email in parsed_response["participants"]:
#     email = email["user_email"]
#     print(email)


# participants.update({name: email})
# print(participants)

# zoom_name = parsed_response["name"]
# zoom_email = parsed_response["user_email"]
# print(zoom_name + " : " + zoom_email)

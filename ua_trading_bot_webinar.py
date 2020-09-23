"""
This will will print the UUID of the past Black Box Trading Webinar
"""

import requests
import json

url = "https://api.zoom.us/v2/webinars/88377897916/registrants?occurrence_id=<string>&status=approved&page_size=110&page_number=1"

payload = {}
headers = {
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIaFZmRTRaTVNZTzloRUpGMkttenVRIiwiZXhwIjoxNjA2MTA0MjM5fQ.DnWPwA3qIvqdRUmVmSfyCA8G_I3rcLJkOXohKkUF2Rw',
  'Cookie': '_zm_lang=en-US; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_date_format=mm/dd/yy; cred=6C64DE3AE923E59D8E69DE88E8BD19B9'
}

response = requests.request("GET", url, headers=headers, data = payload)

# print(response.text.encode('utf8'))

trading_bot_data = response.text.encode('utf8')
# print(response.text.encode('utf8'))
parsed_response = json.loads(trading_bot_data)
# print(parsed_response)

# trading_bot_uuid = parsed_response["webinars"][0]["uuid"]
# print(trading_bot_uuid)


def get_trading_bot_students():
    participants = parsed_response["registrants"]
    # print(participants)
    student_email_name = []
    for students in participants:
        last_name = students["last_name"]
        if last_name in participants:
            student = students["email"], students["last_name"], students["first_name"]
            student_email_name.append(student)
            student_email_name.sort(key=lambda tup: tup[1])
            print("if this prints, the if statement is true")
        else:
            student = students["email"], students["first_name"]
            student_email_name.append(student)
            # sort each member by the name
            student_email_name.sort(key=lambda tup: tup[1])
            print("if this prints, the is statement is not true (printing the else)")
    return student_email_name


get_trading_bot_students()

print(get_trading_bot_students())

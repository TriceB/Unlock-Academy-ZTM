"""
This will print all of the UUIDs from each instance of past Goal Hack Meetings
"""
import requests

url = "https://api.zoom.us/v2/past_meetings/81483069736/instances"

payload = {}
headers = {
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIaFZmRTRaTVNZTzloRUpGMkttenVRIiwiZXhwIjoxNjA2MTA0MjM5fQ.DnWPwA3qIvqdRUmVmSfyCA8G_I3rcLJkOXohKkUF2Rw',
  'Cookie': '_zm_lang=en-US; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_date_format=mm/dd/yy; cred=D86BE0CA56F9E9F3EA8330AE44982BBF'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
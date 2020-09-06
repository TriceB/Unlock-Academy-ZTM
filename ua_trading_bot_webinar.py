"""
This will will print the UUID of the past Black Box Trading Webinar
"""

import requests

url = "https://api.zoom.us/v2/past_webinars/88377897916/instances"

payload = {}
headers = {
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJIaFZmRTRaTVNZTzloRUpGMkttenVRIiwiZXhwIjoxNjA2MTA0MjM5fQ.DnWPwA3qIvqdRUmVmSfyCA8G_I3rcLJkOXohKkUF2Rw',
  'Cookie': '_zm_lang=en-US; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_date_format=mm/dd/yy; cred=716DB724EA5E1D504B627D2B24FBE163'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
'''
This was a test using personal Zoom Account.
Will print the UUID from family Zoom call on Mother's Day
References:
  https://www.w3schools.com/python/python_json.asp
  https://marketplace.zoom.us/docs/guides/guides/postman/using-postman-to-test-zoom-apis
'''

import requests
import json

url = "https://api.zoom.us/v2/meetings/79972553091"

payload = {}
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzUxMiIsInYiOiIyLjAiLCJraWQiOiIxMDc2NzMxOS1kYmUyLTQyZTctOTBmNy00MmE2ZjQ1NTdkMDQifQ.eyJ2ZXIiOjcsImF1aWQiOiI5NDlkYjkxNWVlNTNkMGM4ZTA5MWY2NzM5Y2Q1YzVhMyIsImNvZGUiOiJveHZCRmV4NWVjX29JTklZVEpOUmVLXzhJMjVIbVVjVXciLCJpc3MiOiJ6bTpjaWQ6OU9GTGxpWVBTR0tBRmxuajNVY0JnUSIsImdubyI6MCwidHlwZSI6MCwidGlkIjowLCJhdWQiOiJodHRwczovL29hdXRoLnpvb20udXMiLCJ1aWQiOiJvSU5JWVRKTlJlS184STI1SG1VY1V3IiwibmJmIjoxNTk4Njc3ODQwLCJleHAiOjE1OTg2ODE0NDAsImlhdCI6MTU5ODY3Nzg0MCwiYWlkIjoiYkRCV3o2ckNSMjJkeG1RT0QwNExtUSIsImp0aSI6ImEyMjk4OWNiLTIxNjMtNGU1YS1iNGUwLWMzMTJjY2E0Yzk1MCJ9.oX7HIboHoEXj9CAm7GCR1LVrH6tFYhXmlmM_3xA4x5BuYnc3Vw6lZUfF_SN4_Wc7uq_IsZxmWwAFa-w4hwJB8w',
  'Cookie': '_zm_lang=en-US; _zm_currency=USD; _zm_mtk_guid=16371b47234c4c608b558ff0521fc5fb; _zm_cdn_blocked=log_unblk; cred=F3A7CA3A5251E9DDF79D39856E3E0253'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
zoom_data = response.text.encode('utf8')

parsed_response = json.loads(zoom_data)

zoom_email = parsed_response["host_email"]
print(zoom_email)

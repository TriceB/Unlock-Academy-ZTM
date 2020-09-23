"""
Get a list of everyone who is currently signed up as a student/member

"""
import requests
import json

headers = {
    'accept': 'application/json',
    'X-Auth-API-Key': '1e011ae8048ea138ba511119c4c25734',
    'X-Auth-Subdomain': 'unlockacademy',
}

params = (
    ('page', '1'),
    # as of 9/21 there are a total of 17962 users
    ('limit', '20000'),
)

response = requests.get('https://api.thinkific.com/api/public/v1/users', headers=headers, params=params)

members_response = response.text.encode('utf8')
members_parsed = json.loads(members_response)

# print(members_parsed["items"][1]["email"])


def get_members():
    members = members_parsed["items"]
    members_email_name = []
    for member in members:
        member = member["email"], member["full_name"]
        members_email_name.append(member)
        # this will result in a list of tuples [(email, name), (email, name)]
        # sort by email addresses of tuple which is the 1st element of each tuple
        members_email_name.sort(key=lambda tup: tup[1])
    return members_email_name


get_members()
print(get_members())

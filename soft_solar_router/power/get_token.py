import json
import requests

import getpass


user = input("Enter your email address: ")
password = getpass.getpass("Enter your password: ")
envoy_serial = 122224078323


data = {"user[email]": user, "user[password]": password}
response = requests.post(
    "http://enlighten.enphaseenergy.com/login/login.json?", data=data, verify=False
)
response_data = json.loads(response.text)
data = {
    "session_id": response_data["session_id"],
    "serial_num": envoy_serial,
    "username": user,
}
response = requests.post(
    "http://entrez.enphaseenergy.com/tokens", json=data, verify=False
)
token_raw = response.text
with open("envoy_token.txt", "w") as f:
    f.write(f"TOKEN={token_raw}\n")

print("envoy token logged in envoy_token.txt")

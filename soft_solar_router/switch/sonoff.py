import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import collections
import json
import traceback
import time

from Crypto.Hash import MD5
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from base64 import b64decode, b64encode
from Crypto.Random import get_random_bytes
import json


def format_encryption_msg(payload, api_key, data):
    payload["selfApikey"] = "123"
    # see https://github.com/itead/Sonoff_Devices_DIY_Tools/issues/5)
    iv = generate_iv()
    payload["iv"] = b64encode(iv).decode("utf-8")
    payload["encrypt"] = True

    payload["data"] = encrypt(json.dumps(data, separators=(",", ":")), iv, api_key)


def format_encryption_txt(properties, data, api_key):
    properties["encrypt"] = True

    iv = generate_iv()
    properties["iv"] = b64encode(iv).decode("utf-8")

    return encrypt(data, iv, api_key)


def encrypt(data_element, iv, api_key):
    api_key = bytes(api_key, "utf-8")
    plaintext = bytes(data_element, "utf-8")

    hash = MD5.new()
    hash.update(api_key)
    key = hash.digest()

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded)
    encoded = b64encode(ciphertext)

    return encoded.decode("utf-8")


def decrypt(data_element, iv, api_key):
    api_key = bytes(api_key, "utf-8")
    encoded = data_element

    hash = MD5.new()
    hash.update(api_key)
    key = hash.digest()

    cipher = AES.new(key, AES.MODE_CBC, iv=b64decode(iv))
    ciphertext = b64decode(encoded)
    padded = cipher.decrypt(ciphertext)
    plaintext = unpad(padded, AES.block_size)

    return plaintext


def generate_iv():
    return get_random_bytes(16)


def create_http_session():
    # create an http session so we can use http keep-alives
    http_session = requests.Session()

    # add the http headers
    # note the commented out ones are copies from the sniffed ones
    headers = collections.OrderedDict(
        {
            "Content-Type": "application/json;charset=UTF-8",
            # "Connection": "keep-alive",
            "Accept": "application/json",
            "Accept-Language": "en-gb",
            # "Content-Length": "0",
            # "Accept-Encoding": "gzip, deflate",
            # "Cache-Control": "no-store",
        }
    )

    # needed to keep headers in same order
    http_session.headers = headers

    return http_session


def set_retries(http_session):
    # no retries at moment, control in sonoffdevice
    retries = Retry(
        total=8,
        backoff_factor=0.8,
        allowed_methods=["POST"],
        status_forcelist=None,
    )

    http_session.mount("http://", HTTPAdapter(max_retries=retries))

    return http_session


def get_update_payload(api_key, device_id: str, params: dict):
    import time

    payload = {
        "sequence": str(
            int(time.time() * 1000)
        ),  # otherwise buffer overflow type issue caused in the device
        "deviceid": device_id,
    }

    format_encryption_msg(payload, api_key, params)

    return payload


def send(http_session, request, thefullurl):
    data = json.dumps(request, separators=(",", ":"))
    response = http_session.post(thefullurl, data=data)

    return response


def change_switch(api_key, device_id, ip_address, outlet, on_request):
    strReturn = "OK"
    try:
        http_session = create_http_session()
        http_session = set_retries(http_session)

        if outlet == None:
            # no outlet so we not strip device
            response = send(
                http_session,
                get_update_payload(
                    api_key, device_id, {"switch": on_request, "outlet": int(0)}
                ),
                "http://" + ip_address + ":8081/zeroconf/switch",
            )
        else:
            params = {"switches": [{"switch": "x", "outlet": 0}]}
            params["switches"][0]["switch"] = on_request
            params["switches"][0]["outlet"] = int(outlet)
            response = send(
                http_session,
                get_update_payload(api_key, device_id, params),
                "http://" + ip_address + ":8081/zeroconf/switches",
            )

        response_json = json.loads(response.content.decode("utf-8"))

        if response_json["error"] != 0:
            strReturn = "%s Error returned by device" % response_json["error"]

        return strReturn

    except:
        return "change_switch error setting device %s to state %s : %s" % (
            device_id,
            on_request,
            traceback.format_exc(),
        )


def state_switch(api_key, device_id, ip_address):
    strReturn = "OK"
    try:
        http_session = create_http_session()
        http_session = set_retries(http_session)

        response = send(
            http_session,
            get_update_payload(api_key, device_id, {}),
            "http://" + ip_address + ":8081/zeroconf/info",
        )

        response_json = json.loads(response.content.decode("utf-8"))

        return response_json

    except:
        return "change_switch error setting device %s to state %s : %s" % (
            device_id,
            on_request,
            traceback.format_exc(),
        )


from soft_solar_router.application.interfaces.switch import Switch

import logging

logger = logging.getLogger("sonoff")


class SonOff(Switch):
    ip_address = "192.168.1.50"
    api_key = "5146d9bd-381f-4dfd-bdd5-5972c40eb2b6"
    device_id = "1000bb555e"  # not really required

    state = None

    def __init__(self, ip_address: str, api_key: str, device_id: str) -> None:
        self.ip_address = ip_address
        self.api_key = api_key
        self.device_id = device_id

    def set(self, state: bool) -> None:
        if state != self.state:
            logger.info(f"set switch state to {state}")
            self.state = state
            target_state = "on" if state else "off"
            err = change_switch(
                self.api_key, self.device_id, self.ip_address, None, target_state
            )
            logging.info(err)


# print(err)

"""
def SonoffCallback(device, data):
    print("callback")
    print(device)
    print(data)

    global is_on
    is_on = data["switch"] == "on"

    global listening
    listening = False


dictNewSonoff = {}
dictNewSonoff[device_id] = (api_key, ip_address, outlet)


#BeginMonitoringSonoffDevices(SonoffCallback, dictNewSonoff)


#print(f"switch is {is_on}")



"""

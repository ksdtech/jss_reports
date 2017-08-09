# From: https://github.com/bsquidwrd/JSS-API
#
# This is used to update device names to be the same as the username assigned to the device
#
# You can run this by typing the following:
#       python update_devicename.py
#
# If you have any issues, please submit an issue on this GitHub Repo and
# I can try to help you at the next chance I get.
#
# Set the URL, Username and Password where stated below.
# They currently have placeholders in there, just replace them with your information
#
# For this script, the user you enter must have the following permissions:
#   - Mobile Devices
#       - Read
#       - Write
##

# Python 3.5
import csv
import json
import re
import requests
import sys
import jss_credentials

class JssReports:

    def __init__(self, base_url, user, password, device_names=True, asset_tags=True):
        self.base_url = base_url
        self.user = user
        self.password = password
        self.update_device_names = device_names
        self.update_asset_tags = asset_tags

    def update_device_name(self, device, name):
        url = '{}/mobiledevicecommands/command/DeviceName/{}/id/{}'.format(self.base_url, name, device['id'])
        response = requests.post(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})

        if response.status_code == 201:
            print('Updated device name of {} to {}'.format(device['serial_number'], name))
        else:
            print('Failed to update device name of {}: {}'.format(device['serial_number'], response.text))

    def update_asset_tag(self, device, asset_tag):
        # Apparently JSON PUT is not enabled yet...
        # data = {
        #    'mobile_device': {
        #        'general': {
        #            'id': device['id'],
        #            'asset_tag': asset_tag
        #        }
        #    }
        # }
        # response = requests.put(url, auth=(self.user, self.password),
        #     headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
        #     json=json.dumps(data))

        xmldata = '''<?xml version="1.0" encoding="UTF-8"?>
<mobile_device>
  <general>
    <id>{}</id>
    <asset_tag>{}</asset_tag>
  </general>
</mobile_device>'''.format(device['id'], asset_tag)

        url = '{}/mobiledevices/id/{}'.format(self.base_url, device['id'])
        response = requests.put(url, auth=(self.user, self.password),
            headers={'Content-Type': 'application/xml'}, data=xmldata)
        if response.status_code == 201:
            print('Updated asset_tag of {} to {}'.format(device['serial_number'], asset_tag))
        else:
            print('Failed to update asset_tag of {}: {}'.format(device['serial_number'], response.text))

    def update_devices(self):
        url = '{}/mobiledevices'.format(self.base_url)
        r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
        for obj in r.json()['mobile_devices']:
            username = obj['username']
            device = { 'id': obj['id']
                , 'name': obj['name']
                , 'username': username
                , 'serial_number': obj['serial_number']
                , 'mac_address': obj['wifi_mac_address']
                , 'model': obj['model']
                }

            m = re.match(r'ipad-(\d+)', username)
            if self.update_device_names:
                if m:
                    self.update_device_name(device, username)
                else:
                    print('Not updating device name of {}, username was {}'.format(device['serial_number'], username))

            if self.update_asset_tags:
                ipad_number = int(m.group(1)) if m else 0
                if ipad_number >= 1000:
                    asset_tag = 'A{0:06d}'.format(ipad_number)
                    self.update_asset_tag(device, asset_tag)
                else:
                    print('Not updating asset_tag of {}, username was {}'.format(device['serial_number'], username))


if __name__ == '__main__':
    base_url = jss_credentials.host_url + '/JSSResource'
    reports = JssReports(base_url, jss_credentials.username, jss_credentials.password)
    reports.update_devices()

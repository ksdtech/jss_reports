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

    def __init__(self, base_url, user, password):
        self.base_url = base_url
        self.user = user
        self.password = password

    def update_device_name(self, device, name):
        url = '{}/mobiledevicecommands/command/DeviceName/{}/id/{}'.format(self.base_url, name, device['id'])
        response = requests.post(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})

        if response.status_code == 201:
            print('Updated name of device {} to {}'.format(device['serial_number'], name))
        else:
            print('Failed to update device {}: {}'.format(device['serial_number'], response.text))


    def update_device_names(self):
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
            if re.match(r'ipad-', username):
                self.update_device_name(device, username)
            else:
                print('Not updating device {}, username was {}'.format(device['serial_number'], username))

if __name__ == '__main__':
    base_url = jss_credentials.host_url + '/JSSResource'
    reports = JssReports(base_url, jss_credentials.username, jss_credentials.password)
    reports.update_device_names()

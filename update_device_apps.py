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

    def get_app_by_id(self, app_id):
        url = '{}/mobiledeviceapplications/id/{}'.format(self.base_url, app_id)
        r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
        obj = r.json()['mobile_device_application']
        app = obj['general']
        scope = obj['scope']
        vpp = obj['vpp']
        name = app['name']
        identifier = app['bundle_id']
        print('processing {}'.format(app['name']))
        itunes_store_url = app['itunes_store_url']
        m = re.search(r'\/id(\d+)($|\?)', itunes_store_url)
        if m:
            adam_id = m.group(1)
            d = { 'id': app_id
                , 'name': name
                , 'free': app['free']
                , 'adam_id': adam_id
                , 'identifier': identifier
                , 'link': itunes_store_url
                , 'deploy_automatically': app['deploy_automatically']
                , 'vpp_device_assignment': vpp['assign_vpp_device_based_licenses'] if vpp else False
                , 'vpp_licenses_total': vpp['total_vpp_licenses'] if (vpp and 'total_vpp_licenses' in vpp) else 0
                , 'vpp_licenses_used': vpp['used_vpp_licenses'] if (vpp and 'used_vpp_licenses' in vpp) else 0
                , 'all_mobile_devices': scope['all_mobile_devices']
                , 'mobile_devices': [ user['name'] for user in scope['mobile_devices'] ]
                , 'mobile_device_groups': [ group['name'] for group in scope['mobile_device_groups'] ]
                , 'vpp_assignments': {}
                }
            return d
        else:
            print('could not parse adam_id from url {}'.format(itunes_store_url))
            return None

    def put_vpp_device_assignment(self, app):
        url = '{}/mobiledeviceapplications/id/{}'.format(self.base_url, app['id'])
        data = {
            'mobile_device_application': {
                'general' : {
                    'id': app['id']
                },
                'vpp': {
                    'assign_vpp_device_based_licenses': True,
                    'vpp_admin_account_id': 1,
                }
            }
        }

        r = requests.put(url, auth=(self.user, self.password),
            headers={'Accept': 'application/json'}, json=json.dumps(data))
        print(r.text)


    def update_apps(self):
        url = '{}/mobiledeviceapplications'.format(self.base_url)
        r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
        self.app_ids = [ a['id'] for a in r.json()['mobile_device_applications'] ]
        for app_id in self.app_ids:
            d = self.get_app_by_id(app_id)
            if d and not d['vpp_device_assignment']:
                print(json.dumps(d, indent=2))
                self.put_vpp_device_assignment(d)
                return


if __name__ == '__main__':
    base_url = jss_credentials.host_url + '/JSSResource'
    reports = JssReports(base_url, jss_credentials.username, jss_credentials.password)
    reports.update_apps()

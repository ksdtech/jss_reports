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
        self.vpp_assignment_ids = []
        self.app_ids = []
        self.device_group_ids = []
        self.user_group_ids = []
        self.devices_by_name = { }
        self.devices_by_mac = { }
        self.apps_by_adam = { }
        self.app_user_assignments = { }
        self.device_groups = { }
        self.user_groups = { }


    def get_device_groups(self):
        url = '{}/mobiledevicegroups'.format(self.base_url)
        r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
        self.device_group_ids = [ a['id'] for a in r.json()['mobile_device_groups'] ]
        for device_group_id in self.device_group_ids:
            url = '{}/mobiledevicegroups/id/{}'.format(self.base_url, device_group_id)
            r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
            obj = r.json()['mobile_device_group']
            print('processing {}'.format(obj['name']))
            d = { 'is_smart': obj['is_smart']
                , 'size': len(obj['mobile_devices'])
                }
            self.device_groups[obj['name']] = d


    def get_user_groups(self):
        url = '{}/usergroups'.format(self.base_url)
        r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
        self.user_group_ids = [ a['id'] for a in r.json()['user_groups'] ]
        for user_group_id in self.user_group_ids:
            url = '{}/usergroups/id/{}'.format(self.base_url, user_group_id)
            r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
            obj = r.json()['user_group']
            print('processing {}'.format(obj['name']))
            d = { 'is_smart': obj['is_smart']
                , 'size': len(obj['users'])
                }
            self.user_groups[obj['name']] = d


    # TODO: Where do you find the 'In Use' and 'Reported' numbers?
    # VPP apps can be assigned, but still never used (not in app catalog for instance)
    def get_vpp_assignments(self):
        url = '{}/vppassignments'.format(self.base_url)
        r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
        self.vpp_assignment_ids = [ a['id'] for a in r.json()['vpp_assignments'] ]
        for vpp_assignment_id in self.vpp_assignment_ids:
            url = '{}/vppassignments/id/{}'.format(self.base_url, vpp_assignment_id)
            r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
            obj = r.json()['vpp_assignment']
            vpp_assignment = obj['general']
            vpp_assignment_name = vpp_assignment['name']
            print('processing {}'.format(vpp_assignment_name))
            scope = obj['scope']
            for app in obj['ios_apps']:
                adam_id = str(app['adam_id'])
                app_name = app['name']
                d = { 'app_name': app_name
                    , 'app_adam_id': adam_id
                    , 'vpp_assignment_id': vpp_assignment_id
                    , 'vpp_assignment_name': vpp_assignment_name
                    , 'all_jss_users': scope['all_jss_users']
                    , 'jss_users': [ user['name'] for user in scope['jss_users'] ]
                    , 'jss_user_groups': [ group['name'] for group in scope['jss_user_groups'] ]
                    }
                self.app_user_assignments[adam_id] = d
                if adam_id in self.apps_by_adam:
                    if 'vpp_assignment_name' in self.apps_by_adam[adam_id]['vpp_assignments']:
                        print('app {} already has assignment {}'.format(app_name, self.apps_by_adam[adam_id]['vpp_assignments']['vpp_assignment_name']))
                    else:
                        self.apps_by_adam[adam_id]['vpp_assignments'] = d
                else:
                    print('no app found for {} (adam_id {})'.format(app_name, adam_id))

    def get_devices(self):
        url = '{}/mobiledevices'.format(self.base_url)
        r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
        for obj in r.json()['mobile_devices']:
            device_id = obj['id']
            name = obj['username'] # ipad-1567
            mac_address = obj['wifi_mac_address']
            d = { 'name': name
                , 'mac_address': mac_address
                , 'model': obj['model']
                , 'serial_number': obj['serial_number']
                }
            self.devices_by_name[name] = d
            self.devices_by_mac[mac_address] = d
            url = '{}/mobiledeviceapplications/id/{}'.format(self.base_url, device_id)
            r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
            obj = r.json()['mobile_device']
            for installed_app in obj['applications']:
                identifier = installed_app['identifier']
                if not identifier in self.app_installs_by_identifer:
                    self.app_installs_by_identifer[identifier] = [ ]
                self.app_installs_by_identifer[identifier].append(mac_address)


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
            print(json.dumps(d, indent=2))
            return d
        else:
            print('could not parse adam_id from url {}'.format(itunes_store_url))
            return None

    def get_apps(self):
        url = '{}/mobiledeviceapplications'.format(self.base_url)
        r = requests.get(url, auth=(self.user, self.password), headers={'Accept': 'application/json'})
        self.app_ids = [ a['id'] for a in r.json()['mobile_device_applications'] ]
        for app_id in self.app_ids:
            d = self.get_app_by_id(app_id)
            if d:
                self.apps_by_adam[d['adam_id']] = d

    def collect_all(self):
        self.get_device_groups()
        self.get_user_groups()
        self.get_apps()
        self.get_vpp_assignments()

    def report(self, filename):
        print('Apps still using user assignment ---')
        with open(filename, 'w') as csvfile:
            w = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_ALL)
            w.writerow(['name', 'adam_id', 'identifier', 'link',
                'free', 'deploy_automatically',
                'vpp_device_assignment', 'vpp_licenses_total', 'vpp_licenses_used',
                'scope', 'assignments'])
            for adam_id in self.apps_by_adam:
                app = self.apps_by_adam[adam_id]
                scope = app['mobile_devices'] + app['mobile_device_groups']
                if app['all_mobile_devices']:
                    scope.append('all')
                assignments = []
                if 'jss_users' in app['vpp_assignments']:
                    assignments += app['vpp_assignments']['jss_users']
                if 'jss_user_groups' in app['vpp_assignments']:
                    assignments += app['vpp_assignments']['jss_user_groups']
                if 'all_jss_users' in app['vpp_assignments']:
                    if app['vpp_assignments']['all_jss_users']:
                        assignments.append('all')
                w.writerow([app['name'], app['adam_id'], app['identifier'], app['link'],
                    app['free'], app['deploy_automatically'],
                    app['vpp_device_assignment'], app['vpp_licenses_total'], app['vpp_licenses_used'],
                    ','.join(scope), ','.join(assignments)])


if __name__ == '__main__':
    base_url = jss_credentials.host_url + '/JSSResource'
    reports = JssReports(base_url, jss_credentials.username, jss_credentials.password)
    reports.collect_all()
    reports.report('jss_apps.csv')

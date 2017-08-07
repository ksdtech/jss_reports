# Python 3.5
import csv

class LdifDeviceAdder:

    def __init__(self, replace=False):
        self.device_dn_list = []
        self.replace = replace

    def add_device_members(self):
        print('dn: cn=Devices,ou=Groups,dc=k-ed,dc=net')
        print('changetype: modify')
        for (i, device_dn) in enumerate(self.device_dn_list):
            if i > 0:
                print('-')
            print('add: uniqueMember')
            print('uniqueMember: {}'.format(device_dn))
        print('')


    def update_device(self, ipad_number, site, room, group):
        uid = 'ipad-{}'.format(ipad_number)
        device_dn = 'uid={},ou=People,dc=k-ed,dc=net'.format(uid)
        self.device_dn_list.append(device_dn)
        if self.replace:
            print('dn: {}'.format(device_dn))
            print('changetype: delete')
            print('')
        print('dn: {}'.format(device_dn))
        print('changetype: add')
        print('objectClass: inetOrgPerson')
        print('objectClass: organizationalPerson')
        print('objectClass: person')
        print('objectClass: top')
        print('cn: iPad {}'.format(ipad_number))
        print('givenName: iPad')
        print('mail: {}@kentfieldschools.org'.format(uid))
        print('sn: {}'.format(ipad_number))
        print('uid: {}'.format(uid))
        print('userPassword: aa123456')
        if site:
            print('physicalDeliveryOfficeName: {}'.format(site))
        if room:
            print('roomNumber: {}'.format(room))
        if group:
            print('departmentNumber: {}'.format(group))
            print('employeeType: {}'.format(group))
        print('')

    def process_devices(self, filename):
        with open(filename) as csvfile:
            r = csv.DictReader(csvfile, dialect='excel-tab')
            for row in r:
                self.update_device(row['ipad_number'], row['site'], row['room'], row['group'])
        if not self.replace:
            self.add_device_members()


if __name__ == '__main__':
    adder = LdifDeviceAdder(True)
    adder.process_devices('devices.tsv')

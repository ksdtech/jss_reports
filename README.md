# jss_reports

Some python scripts used for deploying new iPads (and possibly Apple TVs).
Note: you must create a python module 'jss_credentials' with three strings:

* host_url - HTTPS url for your JSS (just 'https://host:port', no trailing slash).
* username - JSS username with API write access
* password - JSS password


## device_ldif.py

Creates "add" or "update" LDIF files for use with ldapmodify or an LDIF-aware
LDAP application, such as [jXplorer](http://jxplorer.org/).  Uses input TSV file
'devices.tsv' to generate two LDIF files:

* people.ldif - device 'inetOrgPerson' records with user names, email addresses, etc.
* devices.ldif - group members for the 'Devices' group


## jss_reports.py

Used this to list information about mobile device apps, vpp assignments, etc. in
a Google sheet.


## update_device_apps.py

Failed attempt to mass-check the "Allow VPP content" checkbox for all apps in
JAMF.


## update_device_name.py

Batch assignment of iPad device names to the username (such as 'ipad-1855').
No TSV file required, uses the usernames already stored in device records.

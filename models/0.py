# -*- coding: utf-8 -*-

from gluon.storage import Storage
settings = Storage()

''' coming soon ...

# max number of mail aliases per domain
settings.maxaliases = 25
# max number of mail address per domain
settings.maxmailboxes = 25
# max quota per domain in MB, 0: infinite
settings.maxquota = 0
# default quota in MB
settings.quota = 1000
'''

# lambda function that returns the maildir 
settings.maildir = lambda r: r['username']+'@'+r['domain']

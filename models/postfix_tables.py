# -*- coding: utf-8 -*-

db.define_table('domain',
    Field('domain','string', length=255, notnull=True, unique=True,),
    Field('description','string', length=255,),
    Field('transport','string', notnull=True, default='virtual', writable=False, readable=False),
    Field('backupmx','boolean', notnull=True, default=False),
    Field('created','datetime', notnull=True, default=request.now, writable=False),
    Field('modified','datetime', notnull=True, update=request.now, writable=False),
    Field('active','boolean', notnull=True, default=True),
    format = '%(domain)s',
    )

''' coming soon ...

    Field('maxaliases','integer', notnull=True, default=settings.maxaliases, 
          comment=T('max # allowed; 0: infinite, -1: disable'),
          label=T('Aliases')),
    Field('maxmailboxes','integer', notnull=True, default=settings.maxmailboxes, 
          comment=T('max # allowed; 0: infinite, -1: disable'),
          label=T('Mailboxes')),
    Field('maxquota','integer', notnull=True, default=0, 
          comment=T('in MB, 0: infinite'),
          label=T('Disk quota')),
    Field('quota','integer', notnull=True, default=0, writable=False, readable=False),
'''
    
db.define_table('domain_alias',
    Field('domain_alias','string', length=255, notnull=True, requires=IS_IN_DB(db, 'domain.domain')), # è necessario?
    Field('domain_target','string', length=255, notnull=True, requires=IS_IN_DB(db, 'domain.domain')),
    Field('created','datetime', notnull=True, default=request.now, writable=False),
    Field('modified','datetime', notnull=True, update=request.now, writable=False),
    Field('active','boolean', notnull=True, default=True),
    )
''' sqlite index example    
# this need to be modified in case mysql or pgsql is used
db.executesql('CREATE UNIQUE INDEX IF NOT EXISTS domain_alias_idx ON domain_alias (domain_alias, domain_target);')
'''

db.define_table('mailbox',
    Field('username','string', length=255, notnull=True,),
    Field('domain','string', length=255, notnull=True, requires=IS_IN_DB(db, 'domain.domain')),
    Field('mail_address','string', length=255, compute=lambda r: r['username']+'@'+r['domain']),
    Field('password','password', length=255, notnull=True,),
    Field('maildir','string', length=255, notnull=True, compute=settings.maildir),
    Field('created','datetime', notnull=True, default=request.now, writable=False),
    Field('modified','datetime', notnull=True, update=request.now, writable=False),
    Field('active','boolean', notnull=True, default=True),
    )
db.mailbox.username.requires=IS_NOT_IN_DB(db(db.mailbox.domain==request.vars.domain), 'mailbox.username', error_message=T('this mail address is already present'))

def mail_passwd(form):
    if form.vars.password:
       import crypt, random
       salt = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(8))
       form.vars.password = crypt.crypt(form.vars.password,'$6$'+salt+'$')

''' coming soon ...
    Field('quota','integer', notnull=True, default=settings.quota),
'''
db.define_table('mail_alias',
    Field('address','string', length=255, notnull=True, unique=True),
    Field('goto','text', notnull=True,),
    Field('created','datetime', notnull=True, default=request.now, writable=False),
    Field('modified','datetime', notnull=True, update=request.now, writable=False),
    Field('active','boolean', notnull=True, default=True),
    )

''' coming soon...
db.define_table('quota',
    Field('username','string'), # TODO: check !!
    Field('bytes','integer', notnull=True, default=0),
    Field('messages','integer', notnull=True, default=0),
    )
'''

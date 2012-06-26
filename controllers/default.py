# -*- coding: utf-8 -*-
#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    title= T('Wellcome to web2postfix')
    if auth.is_logged_in():
        message = CAT(T('Web2postfix is a lightweight web tool to manage virtual mail address with postfix and dovecot.'), UL(
        CAT(A('Domains Administration',_href=URL('domain')),T(' - list and manage domains')),
        CAT(A('Domain Aliases',_href=URL('domain_alias')),T(' - list and manage domain aliases')),
        CAT(A('Mailboxes Administration',_href=URL('mailbox')),T(' - list and manage mailboxes')),
        CAT(A('Mail Aliases',_href=URL('alias')),T(' - list and manage mail address aliases')),
        CAT(A('Administrators Management',_href=URL('admin')),T(' - list and manage administrators')),
        _class='front-menu'))
    else:
        if not db(db.auth_user.id>0).count():
            message = T('Web2postfix is a lightweight web tool to manage virtual mail address with postfix and dovecot. Please register the first administrator. He/she will able to add further users once logged in.')
            form = auth.register()
        else:
            message = T('Web2postfix is a lightweight web tool to manage virtual mail address with postfix and dovecot. Additional users must be registered by an existing administrator. Please log in.')
            form = auth.login()
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
    
@auth.requires_login()
def domain():
    query=((db.domain))
    fields=(db.domain.id,db.domain.domain,
            db.domain.description,db.domain.backupmx,db.domain.active)
    headers={
     }
    return dict(form=SQLFORM.grid(query=query,fields=fields,headers=headers,
         searchable=True,
         sortable=True,
         deletable=True,
         editable=True,
         details=True,
         create=True,
         csv=False,
         paginate=20,
         ))

@auth.requires_login()
def domain_alias():
    query=((db.domain_alias))
    fields=(db.domain_alias.id,db.domain_alias.domain_alias,
            db.domain_alias.domain_target,db.domain_alias.active)
    return dict(form=SQLFORM.grid(query=query,fields=fields,
         searchable=True,
         sortable=True,
         deletable=True,
         editable=True,
         create=True,
         csv=False,
         paginate=20,
         ))

@auth.requires_login()
def mailbox():
    query=((db.mailbox))
    fields=(db.mailbox.id,db.mailbox.mail_address,db.mailbox.domain,db.mailbox.active)
    headers={
     }
    return dict(form=SQLFORM.grid(query=query,fields=fields,headers=headers,
         searchable=True,
         sortable=True,
         deletable=True,
         editable=True,
         details=True,
         create=True,
         csv=False,
         paginate=20,
         ))

@auth.requires_login()
def mail_alias():
    query=((db.mail_alias))
    fields=(db.mail_alias.id,db.mail_alias.address,db.mail_alias.active)
    headers={
     }
    return dict(form=SQLFORM.grid(query=query,fields=fields,headers=headers,
         searchable=True,
         sortable=True,
         deletable=True,
         editable=True,
         details=True,
         create=True,
         csv=False,
         paginate=20,
         ))

@auth.requires_login()
def admin():
    query=((db.auth_user))
    fields=(db.auth_user.id,db.auth_user.first_name,db.auth_user.last_name,db.auth_user.email)
    headers={
     }
    return dict(form=SQLFORM.grid(query=query,fields=fields,headers=headers,
         searchable=True,
         sortable=True,
         deletable=True,
         editable=True,
         details=True,
         create=True,
         csv=False,
         paginate=20,
         ))
         
def docs():
    response.view = 'docs/%s.%s' % (request.args(0), request.extension) if request.args else 'docs/index.html'
    return dict()


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
            message = T('Web2postfix is a lightweight web tool to manage virtual mail address with postfix and dovecot. Please register the first administrator. He/she will be able to add further users once logged in.')
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
    deletable=False
    js=''
    db.domain.maxmailboxes.represent = lambda value,row: \
      SPAN(str(db(db.mailbox.domain==row.domain).count('id'))+'/'+str(row.maxmailboxes))+' ' \
      if row.type=='full' else '-'
    db.domain.maxaliases.represent = lambda value,row: \
      SPAN(str(db(db.mail_alias.domain==row.domain).count('id'))+'/'+str(row.maxaliases))+' ' \
      if row.type=='full' else '-'
    query=((db.domain))
    fields=(db.domain.id,db.domain.domain,db.domain.type,db.domain.maxmailboxes,\
    	db.domain.maxaliases,db.domain.active)
    headers={}
    links = [\
      lambda row: A('Manage mailboxes',\
      _href=URL('mailbox',vars=dict(keywords='mailbox.domain="'+row.domain+'"'))) \
      if row.type=='full' else '',
      lambda row: A('Manage mail alias',\
      _href=URL('mail_alias',vars=dict(keywords='mail_alias.domain="'+row.domain+'"'))) \
      if row.type=='full' else '',
      lambda row: A('Manage target domain',\
      _href=URL("domain_alias",vars=dict(keywords='domain_alias.domain_alias="'+row.domain+'"'))) \
      if row.type=='alias' else '']
    try:
        if request.args[0]=='edit':
            db.domain.id.readable=False
            db.domain.maxmailboxes.represent = None
            db.domain.maxaliases.represent = None
            deletable=True
            links = []
        elif request.args[0]=='view':
            db.domain.id.readable=False
            db.domain.maxmailboxes.represent = lambda value,row: \
              SPAN(str(db(db.mailbox.domain==row.domain).count('id'))+'/'+str(row.maxmailboxes))+' '\
               if row.type=='full' else '-'
            db.domain.maxmailboxes.comment=T('existing mailboxes / max # allowed')
            db.domain.maxaliases.represent = lambda value,row: \
              SPAN(str(db(db.mail_alias.domain==row.domain).count('id'))+'/'+str(row.maxaliases))+' '\
               if row.type=='full' else '-'
            db.domain.maxaliases.comment=T('existing mail alias / max # allowed')
        if request.args[0]=='edit' or request.args[0]=='new':
            js=SCRIPT("$(document).ready(function(){\
                if ($('#domain_type').val()=='alias'){\
                        jQuery('#domain_maxaliases__row').hide();\
                        jQuery('#domain_maxmailboxes__row').hide();\
                        jQuery('#domain_maxquota__row').hide();\
                    };\
                $('#domain_type').change(function(){\
                    if($('#domain_type').val()=='full'){\
                        jQuery('#domain_maxaliases__row').show('slow');\
                        jQuery('#domain_maxmailboxes__row').show('slow');\
                        jQuery('#domain_maxquota__row').show('slow');\
                    } else { \
                        jQuery('#domain_maxaliases__row').hide('slow');\
                        jQuery('#domain_maxmailboxes__row').hide('slow');\
                        jQuery('#domain_maxquota__row').hide('slow');\
                }})});")
    except:
        pass

    return dict(
        form=SQLFORM.grid(query=query,
#          left=db.domain.on(db.domain_alias.domain_alias==db.domain.domain),
          fields=fields,
          headers=headers,
          links=links,
          searchable=True,
          sortable=True,
          deletable=deletable,
          editable=True,
          details=True,
          create=True,
          csv=False,
          paginate=20,
          ),
        js=js)

@auth.requires_login()
def domain_alias():
    deletable=False
    selected_domain = None
    try:
        if request.vars.keywords:
            import re
            selected_domain = re.search(r'domain_alias\.domain_alias="([.a-z0-9]*)"',\
              request.vars.keywords).group(1)
        if request.args[0]=='view':
            db.domain_alias.id.readable=False
        if request.args[0]=='edit':
            db.domain_alias.id.readable=False
            db.domain_alias.domain_alias.writable=False
            deletable=True
        if request.args[0]=='new':
            existing_alias = db()._select(db.domain_alias.domain_alias)
            db.domain_alias.domain_alias.requires=IS_IN_DB(db((db.domain.type=='alias')&(~db.domain.domain.belongs(existing_alias))),'domain.domain')
            db.domain_alias.domain_alias.default = selected_domain
    except:
        pass
    # ugly check
    try:
        test=request.args[0]
    except:
        if selected_domain != None:
            target_not_exist = db(db.domain_alias.domain_alias==selected_domain).isempty()
            if target_not_exist:
              response.flash=T('No target domain has been set for this domain alias. Please add it.')
    query=((db.domain_alias))
    fields=(db.domain_alias.id,db.domain_alias.domain_alias,
            db.domain_alias.domain_target,db.domain_alias.active)
    return dict(form=SQLFORM.grid(query=query,fields=fields,
         searchable=True,
         sortable=True,
         editable=True,
         create=True,
         deletable=deletable,
         csv=False,
         paginate=20,
         ))

@auth.requires_login()
def mailbox():
    selected_domain = None
    try:
        if request.vars.keywords:
            import re
            selected_domain = re.search(r'mailbox\.domain="([.a-z0-9]*)"',\
              request.vars.keywords).group(1)
        if request.args[0]=='edit' or request.args[0]=='view':
            db.mailbox.id.readable=False
        elif request.args[0]=='new':
            db.mailbox.domain.default = selected_domain
    except:
        pass
    if request.args and request.args[0]=='view':
            db.mailbox.password.readable=False
            db.mailbox.mail_address.readable=True
            db.mailbox.maildir.readable=True
    query=((db.mailbox))
    fields=(db.mailbox.id,db.mailbox.mail_address,db.mailbox.maildir,db.mailbox.domain,db.mailbox.active)
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
         onvalidation=mail_passwd,
         paginate=20,
         ))

@auth.requires_login()
def mail_alias():
    selected_domain = None
    try:
        if request.vars.keywords:
            import re
            selected_domain = re.search(r'mail_alias\.domain="([.a-z0-9]*)"',\
              request.vars.keywords).group(1)
        if request.args[0]=='edit' or request.args[0]=='view':
            db.mail_alias.id.readable=False
        elif request.args[0]=='new':
            db.mail_alias.domain.default = selected_domain
    except:
        pass
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


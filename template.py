import xmlrpclib

username = 'admin'
pwd = 'admin'      #the password of the user
dbname = 'askme;)'    #the database name before ".my.openerp.com" on the openerp SaaS
url = "http://127.0.0.1"
#http://127.0.0.1:8069 this is DB url
# /xmlrpc/common is webservice for logging in
# Get the uid
sock_common = xmlrpclib.ServerProxy(url+'/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)

#/xmlrpc/object This is model webservice
##replace localhost with the address of the server

sock = xmlrpclib.ServerProxy(url+'/xmlrpc/object')

#Searching All Product
#ids = sock.execute(dbname, uid, pwd, 'sale.order', 'search', [])

#Then, reading all the Product Detail from databse
records = sock.execute(dbname, uid, pwd, 'ir.actions.report.xml', 'search', [])

#Searching All Product
ids = sock.execute(dbname, uid, pwd, 'ir.actions.report.xml', 'search', [])
ids = sorted(ids)
reports = sock.execute(dbname, uid, pwd, 'ir.actions.report.xml', 'read', ids, ['name', 'report_rml_content'])

#fl = open('some.rml', 'r')
#rml = fl.read()
#fl.close()
#print rml
for report in reports:
    print "############", report['id'],report['name']
#    if report['id'] == 424:
#        print "#############\n\n", report['report_rml_content']
#        print sock.execute(dbname, uid, pwd, 'ir.actions.report.xml', 'write', [report['id']], {'report_rml_content': rml})

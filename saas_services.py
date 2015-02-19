import xmlrpclib

username = 'admin' #the user
pwd = 'admin'      #the password of the user
dbname = 'label'    #the database name before ".odoo.com" or ".my.openerp.com" on the odoo/openerp SaaS
url = "http://127.0.0.1:8069"
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
records = sock.execute(dbname, uid, pwd, 'ir.actions.report', 'search', [])

print records

for l in sock.execute(dbname, uid, pwd, 'ir.actions.report', 'read', records):
    print"@@@@@", l['id'], l['name']

#    x = sock.execute(dbname, uid, pwd, 'sale.order.line', 'read', l, ['name'])
#    print x

#print  sock.execute(dbname, uid, pwd, 'sale.order.line', 'unlink', [109, 110])

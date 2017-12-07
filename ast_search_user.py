#!/usr/bin/env python

import cgi
#import cgitb
#cgitb.enable()

import asterisk.manager
import json

import MOD_html_funcs
import MOD_ast_funcs


#########################################################################################################################################
# Contact Variables
data = json.load(open('/etc/my_json.json'))
HOSTNAME = str(data["ami"]["hostname"])
AMI_USER = str(data["ami"]["username"])
AMI_PASS = str(data["ami"]["password"])


#########################################################################################################################################
# Print HTML
MOD_html_funcs.print_html_header()
MOD_html_funcs.print_html_navbar()

#########################################################################################################################################
try:
	username = ""
	extension = ""
	dn = ""

	form = cgi.FieldStorage()
	if "username" in form:
		username = form["username"].value
	else:
		username = ""

	#username = "akalfas"

	connector = MOD_ast_funcs.ast_ami_connect(HOSTNAME,AMI_USER,AMI_PASS)
	if username == "":
		command = "sip show peers"
		result = MOD_ast_funcs.ast_peer_info(connector,command)
	else:
		command = "sip show peer "+username
		result = MOD_ast_funcs.ast_peer_info(connector,command)
		logging = MOD_ast_funcs.ast_get_log(username)
		ip_address = result[4]
		ip_info = MOD_ast_funcs.get_ip_info(ip_address)

except:
	pass


#########################################################################################################################################
# Print HTML
MOD_html_funcs.print_html_search_user()


if username == "":
	print '<div class="container">'
	print '<div align="right"><b><i>user count = %s</i></b><div>' % (len(result))

	print '<table class="table table-hover">'
	print '<thead>'
	print '<tr><th>Username</th><th>IP Address</th><th>Connection Info</th></tr>'
	print '</thead>'
	print '<tbody>'
	if result != None:
		for res in result:
			print '<tr>'
			print '<td>%s</td>' % (res[0])
			print '<td>%s</td>' % (res[1])
			print '<td>%s</td>' % (res[2])
			print '</tr>'
	print '</tbody>'
	print '</table>'
else:
	print '<div class="container">'
	print '<table class="table table-hover table-bordered">'
	print '<thead>'
	print '<tr><th>Username</th><th>LDAP extension</th><th>CallerID</th><th>Context</th><th>IP Address</th><th>DTMF</th><th>Client</th><th>Status</th></tr>'
	print '</thead>'
	print '<tbody>'
	if result != None:
		print '<tr>'
		print '<td>%s</td>' % (result[0])
		print '<td>%s</td>' % (result[1])
		print '<td>%s</td>' % (result[2])
		print '<td>%s</td>' % (result[3])
		print '<td>%s</td>' % (result[4])
		print '<td>%s</td>' % (result[5])
		print '<td>%s</td>' % (result[6])
		print '<td>%s</td>' % (result[7])
		print '</tr>'
	print '</tbody>'
	print '</table>'
	print '<h5><b><i>*IP address info: %s, %s, %s</i></b></h5>' % (ip_info[1],ip_info[2],ip_info[3])
	print '</div>'
	
	print '<h4><center>Logging Information</center></h4>'
	print '<div class="container" style="border:1px solid #cecece;overflow-y:scroll;height:500px;width:1200px;" >'
	print '<div class="contect">'
	#print "<b>Logging Information:</b><br><br>"
	for log in logging:
		print log+"<br>"
	print '</div>'
	print '</div>'

#!!! Dont forget manager.logoff()


# Print HTML
MOD_html_funcs.print_html_tail()


#########################################################################################################################################



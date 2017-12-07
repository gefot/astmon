#!/usr/bin/env python

import datetime
import cgi
#import cgitb
#cgitb.enable()

import MySQLdb as mariadb
import json

import MOD_html_funcs


#########################################################################################################################################
# Contact Variables
data = json.load(open('/etc/my_json.json'))
DB_HOST = str(data["db"]["db_host"])
DB_USERNAME = str(data["db"]["db_username"])
DB_PASSWORD = str(data["db"]["db_password"])
DB = str(data["db"]["db"])


#########################################################################################################################################
# Print HTML
MOD_html_funcs.print_html_header()
MOD_html_funcs.print_html_navbar()


#########################################################################################################################################
try:
	## Measure Script Execution
	start = datetime.datetime.now()

	#startdate = ""
	#srcnum = ""
	#dstnum = ""

	form = cgi.FieldStorage()
	if "startdate" in form:
		startdate = form["startdate"].value[:4]+"-"+form["startdate"].value[4:6]+"-"+form["startdate"].value[6:]
	else:
		startdate = ""
	if "srcnum" in form:
		srcnum = form["srcnum"].value
	else:
		srcnum = ""
	if "dstnum" in form:
		dstnum = form["dstnum"].value
	else:
		dstnum = ""

	if startdate != "" or srcnum != "" or dstnum != "":
		do_search = True
	else:
		do_search = False


	if do_search:
		conn = mariadb.connect(DB_HOST,DB_USERNAME,DB_PASSWORD,DB)
		cur = conn.cursor()
		query = "SELECT calldate,src,dst,userfield,duration,disposition FROM cdr WHERE calldate LIKE '%%%s%%' AND src LIKE '%%%s%%' AND dst LIKE '%%%s%%' ORDER By calldate desc" % (startdate,srcnum,dstnum)
		cur.execute(query)
		rows = cur.fetchall()
		cur.close()
		conn.close()


	## Measure Script Execution
	endtime = datetime.datetime.now()-start

except Exception as ex:
	print ex


#########################################################################################################################################
# Print HTML
MOD_html_funcs.print_html_search_cdr()

# 1st Container
print '<div class="container-fluid">'
print '<table class="table table-hover">'
print '<thead>'
print '<tr><th>Date</th><th>Source Number</th><th>Destination Number</th><th>Username</th><th>Duration</th><th>Type</th></tr>'
print '</thead>'
print '<tbody>'
for row in rows:
	print '<tr>'
	for i,field in enumerate(row):
		print '<td>%s</td>' % (field)
	print '</tr>'
print '</tbody>'
print '</table>'
print '<i>total entries = %s</i><br>' % (len(rows))
print '<i>execution time = %s</i><br>' % (endtime)
print '</div>'


# Print HTML
MOD_html_funcs.print_html_tail()


#########################################################################################################################################

#!/usr/bin/env python

import time,datetime
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
	if "queuename" in form:
		queuename = form["queuename"].value
	else:
		queuename = ""
	if "agent" in form:
		agent = form["agent"].value
	else:
		agent = ""

	do_search = False
	if startdate != "":
		do_search = True
	else:
		do_search = False


	if do_search:
		conn = mariadb.connect(DB_HOST,DB_USERNAME,DB_PASSWORD,DB)
		cur = conn.cursor()

		#Answered calls statistics
		query = "SELECT data1,data2,agent FROM queuelog WHERE (event LIKE '%%COMPLETE%%' AND queuename LIKE '%%%s%%' AND time LIKE '%%%s%%' AND agent LIKE '%%%s%%' )" % (queuename,startdate,agent)
		cur.execute(query)
		rows = cur.fetchall()
		total_answered_calls = len(rows)
		total_queue_duration = sum(int(i[0]) for i in rows)
		total_talk_duration = sum(int(i[1]) for i in rows)
		#print "total_answered_calls = ",total_answered_calls
		#print "total_queue_duration = ",total_queue_duration
		#print "total_talk_duration = ",total_talk_duration
		#print "<hr>"

		# Missed call statistics
		query = "SELECT data3 FROM queuelog WHERE ((event LIKE '%%ABANDON%%' OR event LIKE '%%EXITWITHTIMEOUT%%') AND queuename LIKE '%%%s%%' AND time LIKE '%%%s%%')" % (queuename,startdate)
		cur.execute(query)
		rows = cur.fetchall()
		total_missed_calls = len(rows)
		total_missed_duration = sum(int(i[0]) for i in rows)
		#print "total_missed_calls = ",total_missed_calls
		#print "total_missed_duration = ",total_missed_duration
		#print "<hr>"

		# Answered calls
		query = "SELECT time,callid,queuename,agent,data1,data2 FROM queuelog WHERE (time LIKE '%s%%' AND event LIKE '%%COMPLETE%%' AND queuename LIKE '%%%s%%' and agent LIKE '%%%s%%') ORDER By time desc" % (startdate,queuename,agent)
		cur.execute(query)
		rows = cur.fetchall()
		answered_calls_list = []
		for row in rows:
			#print row[1]
			query_child = "SELECT time,data2 from queuelog WHERE (time LIKE '%s%%' AND callid LIKE %s AND event LIKE '%%ENTERQUEUE%%')" % (startdate,row[1])
			cur.execute(query_child)
			rows_child = cur.fetchall()
			callerID = rows_child[0][1]
			#callerID = "99999"
			my_queue = time.strftime("%M:%S", time.gmtime(int(row[4])))
			my_talk = time.strftime("%M:%S", time.gmtime(int(row[5])))
			my_call = [row[0],row[2],row[3],callerID,my_queue,my_talk]
			#print my_call
			#print "<br>"
			answered_calls_list.append(my_call)

		# Missed calls
		query = "SELECT time,callid,queuename,data3 FROM queuelog WHERE ((event LIKE '%%ABANDON%%' OR event LIKE '%%EXITWITHTIMEOUT%%') AND time LIKE '%%%s%%' AND queuename LIKE '%%%s%%') ORDER By time desc" % (startdate,queuename)
		cur.execute(query)
		rows = cur.fetchall()
		missed_calls_list = []
		for row in rows:
			query_child = "SELECT time,data2 from queuelog WHERE (time LIKE '%s%%' AND callid LIKE %s AND event LIKE '%%ENTERQUEUE%%')" % (startdate,row[1])
			cur.execute(query_child)
			rows_child = cur.fetchall()
			callerID = rows_child[0][1]
			#callerID = "99999"
			my_queue = time.strftime("%M:%S", time.gmtime(int(row[3])))
			my_call = [row[0],row[2],callerID,my_queue]
			#print my_call
			#print "<br>"
			missed_calls_list.append(my_call)

		cur.close()
		conn.close()

		## Measure Script Execution
		endtime = datetime.datetime.now()-start

except Exception as ex:
	print "Exception = ",ex



#########################################################################################################################################
# Print HTML
MOD_html_funcs.print_html_search_queue()

# 1st Container
print '<div class="container">'
if do_search:
	print '<h3><center><b>Answered Calls</b></center></h3>'
	print '<table class="table table-hover">'
	print '<thead>'
	print '<tr><th>Date</th><th>Queue</th><th>Agent</th><th>CallerID</th><th>Queue Time</th><th>Talk Time</th></tr>'
	print '</thead>'
	print '<tbody>'
	for row in answered_calls_list:
		print '<tr>'
		for i,field in enumerate(row):
			print '<td>%s</td>' % (field)
		print '</tr>'
	print '</tbody>'
	print '</table>'
	print '<i>Total Calls = %s</i><br>' % total_answered_calls
	print '<i>Total Talk Time = %s</i><br>' % time.strftime("%H:%M:%S", time.gmtime(int(total_talk_duration)))
	print '<i>Total Queue Time = %s</i><br>' % time.strftime("%H:%M:%S", time.gmtime(int(total_queue_duration)))
	print '<i>execution time = %s</i><br>' % (endtime)

	print '<hr>'
	print '<hr>'
	print '<h3><center><b>Missed Calls</b></center></h3>'
	print '<table class="table table-hover">'
	print '<thead>'
	print '<tr><th>Date</th><th>Queue</th><th>CallerID</th><th>Queue Time</th></tr>'
	print '</thead>'
	print '<tbody>'
	for row in missed_calls_list:
		print '<tr>'
		for i,field in enumerate(row):
			print '<td>%s</td>' % (field)
		print '</tr>'
	print '</tbody>'
	print '</table>'
	print '<i>Total Calls = %s</i><br>' % total_missed_calls
	print '<i>Total Queue Time = %s</i><br>' % time.strftime("%H:%M:%S", time.gmtime(int(total_missed_duration)))
	print '<i>execution time = %s</i><br>' % (endtime)

print '</div>'


# Print HTML
MOD_html_funcs.print_html_tail()


#########################################################################################################################################

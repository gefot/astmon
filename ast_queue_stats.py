#!/usr/bin/env python

import time,datetime

import MySQLdb as mariadb
import json



#########################################################################################################################################
# Contact Variables
data = json.load(open('/etc/my_json.json'))
DB_HOST = str(data["db"]["db_host"])
DB_USERNAME = str(data["db"]["db_username"])
DB_PASSWORD = str(data["db"]["db_password"])
DB = str(data["db"]["db"])
AST_QUEUE_STATS_FILE = str(data["queues"]["ast_queue_stats"])


#########################################################################################################################################
try:
	## Measure Script Execution
	start = datetime.datetime.now()

	my_file = open(AST_QUEUE_STATS_FILE,"w")

	conn = mariadb.connect(DB_HOST,DB_USERNAME,DB_PASSWORD,DB)
	cur = conn.cursor()

	startdate = str(datetime.datetime.now().date())
	queues = ["authnet","accounts","sis","gram","dir"]
	all_answered_calls = 0
	all_talk_duration = 0 
	all_avg_talk_per_call = 0
	all_queue_duration = 0
	all_missed_calls = 0

	for queuename in queues:
		print "\nqueuename =",queuename
		query = "SELECT data1,data2,agent FROM queuelog WHERE (event LIKE '%%COMPLETE%%' AND queuename LIKE '%%%s%%' AND time LIKE '%%%s%%' )" % (queuename,startdate)
		cur.execute(query)
		rows = cur.fetchall()
		total_answered_calls = len(rows)
		total_talk_duration = sum(int(i[1]) for i in rows)
		total_talk_duration_f = time.strftime("%H:%M:%S", time.gmtime(int(total_talk_duration)))
		if total_answered_calls > 0:
			avg_talk_per_call = total_talk_duration / total_answered_calls
			avg_talk_per_call_f = time.strftime("%H:%M:%S", time.gmtime(int(avg_talk_per_call)))
		else:
			avg_talk_per_call_f = "0:00"
		total_queue_duration = sum(int(i[0]) for i in rows)
		total_queue_duration_f = time.strftime("%H:%M:%S", time.gmtime(int(total_queue_duration)))
		print "total_answered_calls = ",total_answered_calls
		print "total_talk_duration = ",total_talk_duration_f
		print "avg_talk_per_call = ",avg_talk_per_call_f
		print "total_queue_duration = ",total_queue_duration_f
		query = "SELECT data3 FROM queuelog WHERE ((event LIKE '%%ABANDON%%' OR event LIKE '%%EXITWITHTIMEOUT%%') AND queuename LIKE '%%%s%%' AND time LIKE '%%%s%%')" % (queuename,startdate)
		cur.execute(query)
		rows = cur.fetchall()
		total_missed_calls = len(rows)
		print "total_missed_calls = ",total_missed_calls

		file_string = "%s %d %s %s %s %d\n" % (queuename, total_answered_calls, total_talk_duration_f, avg_talk_per_call_f, total_queue_duration_f, total_missed_calls)
		#file_string = "%s" % (queuename)
		my_file.write(file_string)

		# Sum metrics from all queues
		all_answered_calls += total_answered_calls
		all_talk_duration += total_talk_duration
		all_talk_duration_f = time.strftime("%H:%M:%S", time.gmtime(int(all_talk_duration)))
		all_avg_talk_per_call += avg_talk_per_call
		all_queue_duration += total_queue_duration
		all_queue_duration_f = time.strftime("%H:%M:%S", time.gmtime(int(all_queue_duration)))
		all_missed_calls += total_missed_calls

	# Write sum metrics to file
	all_avg_talk_per_call /= 5
	all_avg_talk_per_call_f = time.strftime("%H:%M:%S", time.gmtime(int(all_avg_talk_per_call)))

	file_string = "%s %d %s %s %s %d\n" % ("TOTAL", all_answered_calls, all_talk_duration_f, all_avg_talk_per_call_f, all_queue_duration_f, all_missed_calls)
	my_file.write(file_string)

	my_file.close()
	cur.close()
	conn.close()


	## Measure Script Execution
	endtime = datetime.datetime.now()-start

except Exception as ex:
	print "Exception = ",ex


#########################################################################################################################################



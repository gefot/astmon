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
AST_QUEUE_STATS_FILE = str(data["queues"]["ast_queue_stats"])


#########################################################################################################################################
# Print HTML
MOD_html_funcs.print_html_header_auto_ref()
#MOD_html_funcs.print_html_header()
MOD_html_funcs.print_html_navbar()


#########################################################################################################################################
try:

	form = cgi.FieldStorage()
	if "queuename" in form:
		queuename = form["queuename"].value
	else:
		queuename = ""

	all_agents = []
	all_calls_waiting =[]
	connector = MOD_ast_funcs.ast_ami_connect(HOSTNAME,AMI_USER,AMI_PASS)
	queues = ["authnet","accounts","sis","gram","dir"]
	agent_ready_text = ""

	for my_queuename in queues:
		command = "queue show "+my_queuename
		my_agents, my_calls_waiting = MOD_ast_funcs.ast_queue_info(connector,command)

		# Search if there is a "Ready" agent for each queue. Otherwise print alert message.
		ready_agents = False
		for my_agent in my_agents:
			if my_agent[3] == "Ready":
				ready_agents = True

		if ready_agents == False:
			agent_ready_text += "!!! No available agent in queue \"%s\" !!!<br>" % my_queuename

		all_agents.append(my_agents)
		all_calls_waiting.append(my_calls_waiting)

except:
	pass


#########################################################################################################################################
# Print HTML
MOD_html_funcs.print_html_nav_pills()


#########################################################################################################################################
# 1st Container
# Show queue stats
try:
	stat_list = []
	my_file = open(AST_QUEUE_STATS_FILE,"r")
	for line in my_file.readlines():
		line = line.rstrip('\n')
		stat_item = line.split(" ")
		if queuename == "":
			stat_list.append(stat_item)
		else:
			if stat_item[0] == queuename:
				stat_list.append(stat_item)
except:
	pass

#print '<div class="container" style="max-width:1200px">'
print '<div class="container">'
print '<table class="table table-bordered table-striped">'
print '<thead">'
print '<tr><th style="width:16%">Queuename</th><th style="width:16%">Total Calls</th><th style="width:16%">Total Duration</th><th style="width:16%">Avg Duration per Call</th><th style="width:16%">Total Queue Time</th><th style="width:16%">Total Missed Calls</th></tr>'
print '</thead>'
print '<tbody>'

for stat in stat_list:
	print '<tr>'
	print '<td>%s</td>' % (stat[0])
	print '<td>%s</td>' % (stat[1])
	print '<td>%s</td>' % (stat[2])
	print '<td>%s</td>' % (stat[3])
	print '<td>%s</td>' % (stat[4])
	print '<td>%s</td>' % (stat[5])
	print '</tr>'

print '</tbody>'
print '</table>'
print '</div>'


#########################################################################################################################################
# 2nd Container
print '<div class="container">'
print '<div class="row">'

print '<div class="col-lg-4">'
# Show alerts
if agent_ready_text != "":
	print """
	<br><br>
	<div class="alert-danger">
	<strong><center>%s</center></strong>
	</div>
	<br>
	""" % (agent_ready_text)
else:
	print """
	<br><br>
	<div class="alert-success">
	<strong><center>All queues have at least one available agent</center></strong>
	</div>
	<br>
	"""

# Show calls in queue
print '<table class="table">'
print '<thead>'
print '<tr><th>Calls in Queue</th><th>Time Queued</th></tr>'
print '</thead>'
print '<tbody>'
for calls_waiting in all_calls_waiting:
	if calls_waiting != []:
		for i,call in enumerate(calls_waiting):
			if queuename == "":
				print '<tr>'
				print '<td>%s</td>' % (call[0])
				print '<td>%s</td>' % (call[1])
				print '</tr>'
			else:
				if call[0] == queuename:
					print '<tr>'
					print '<td>%s</td>' % (call[0])
					print '<td>%s</td>' % (call[1])
					print '</tr>'
print '</tbody>'
print '</table>'
print '</div>'


# Show list of agents per queue (or all queues if "all queues" is selected)
print '<div class="col-lg-4">'
print '<table class="table">'
print '<thead>'
print '<tr><th>Agent</th><th>Queue</th><th>State</th></tr>'
print '</thead>'
print '<tbody>'
for agent_list in all_agents:
	if agent_list != None:
		for agent in agent_list:
			if queuename == "":
				if agent[0] == 1:
					print '<tr class="bg-primary">'
					print '<td>%s</td>' % (agent[1])
					print '<td>%s</td>' % (agent[2])
					print '<td>%s</td>' % (agent[3])
					print '</tr>'
				if agent[0] == 2:
					print '<tr class="bg-success">'
					print '<td>%s</td>' % (agent[1])
					print '<td>%s</td>' % (agent[2])
					print '<td>%s</td>' % (agent[3])
					print '</tr>'
				if agent[0] == 3:
					print '<tr class="bg-danger">'
					print '<td>%s</td>' % (agent[1])
					print '<td>%s</td>' % (agent[2])
					print '<td>%s</td>' % (agent[3])
					print '</tr>'
			else:
				if agent[2] == queuename:
					if agent[0] == 1:
						print '<tr class="bg-primary">'
						print '<td>%s</td>' % (agent[1])
						print '<td>%s</td>' % (agent[2])
						print '<td>%s</td>' % (agent[3])
						print '</tr>'
					if agent[0] == 2:
						print '<tr class="bg-success">'
						print '<td>%s</td>' % (agent[1])
						print '<td>%s</td>' % (agent[2])
						print '<td>%s</td>' % (agent[3])
						print '</tr>'
					if agent[0] == 3:
						print '<tr class="bg-danger">'
						print '<td>%s</td>' % (agent[1])
						print '<td>%s</td>' % (agent[2])
						print '<td>%s</td>' % (agent[3])
						print '</tr>'
print '</tbody>'
print '</table>'
print '</div>'

print '<div class="col-lg-4">'
print '</div>'

print '</div>'
print '</div>'



# Print HTML
MOD_html_funcs.print_html_tail()



#########################################################################################################################################

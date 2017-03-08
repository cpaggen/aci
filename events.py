# simple, very simple code to obtain a subscription channel to _all_ ACI events
# this uses ACIToolkit which handles callbacks/websocket/queues/threads
#
# cpaggen

import smtplib
import json
from acitoolkit.acitoolkit import *
from websocket import *
import email.utils
from email.mime.text import MIMEText
import os
import sys

    
try:  
    password = os.environ["ACI-password"]
except KeyError:
    print "Please set the ACI-password environment variable"
    sys.exit(1)

def sendMail(mailFrom,mailTo,subject,text,server):
    msg = MIMEText(text)
    msg['To'] = email.utils.formataddr(('Recipient', mailTo))
    msg['From'] = email.utils.formataddr(('ACI in the lab', mailFrom))
    msg['Subject'] = 'ACI event for tenant TEN-01!'
    server = smtplib.SMTP(server)
    server.sendmail(mailFrom,mailTo,msg.as_string())
    server.quit()

session = Session("https://10.50.139.156", "admin", password)
session.login()

print session.token

sub_url = '/api/node/class/fvTenant.json?query-target-filter=and(eq(fvTenant.name,"TEN-01"))&query-target=subtree&subscription=yes'

session.subscribe(sub_url)

while True:
    if session.has_events(sub_url):
        print "--- New event ---"
        event = session.get_event(sub_url)
        print event
	sendMail("aci@cpoclon.cisco.com","aleza@cisco.com","ACI event!",json.dumps(event),"mail.cisco.com")

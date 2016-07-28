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

def sendMail(mailFrom,mailTo,subject,text,server):
    msg = MIMEText(text)
    msg['To'] = email.utils.formataddr(('Recipient', mailTo))
    msg['From'] = email.utils.formataddr(('ACI in the lab', mailFrom))
    msg['Subject'] = 'ACI event!'
    server = smtplib.SMTP(server)
    server.sendmail(mailFrom,mailTo,msg.as_string())
    server.quit()

session = Session("https://10.48.58.5", "sdn", "cisco")
session.login()

print session.token

sub_url = '/api/node/class/fvTenant.json?query-target-filter=and(eq(fvTenant.name,"cpaggen"))&query-target=subtree&subscription=yes'

session.subscribe(sub_url)

while True:
    if session.has_events(sub_url):
        print "--- New event ---"
        event = session.get_event(sub_url)
        print event
	sendMail("aci@mylab.cisco.com","cpaggen@cisco.com","ACI event!",json.dumps(event),"mail.cisco.com")

#!/usr/bin/env Python
#
# cpaggen
#
# no error checks - this is a very simple REST API 'poster' that pushes data to APIC
#

import requests
import sys
import json
from pprint import pprint
import time

http_header={"User-Agent" : "Chrome/17.0.963.46",
             "Accept" : "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,text/png,*/*;q=0.5",
             "Accept-Language" : "en-us,en;q=0.5",
             "Accept-Charset" : "ISO-8859-1",
             "Content-type": "application/x-www-form-urlencoded"
            }

def getAPICCookie(ip_addr, username, password):
    url = 'http://'+ip_addr+'/api/aaaLogin.xml'

    http_header["Host"]=ip_addr
    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (username, password)
    req = requests.post(url, data=xml_string, headers=http_header, verify=False)
    rawcookie=req.cookies['APIC-cookie']
    return rawcookie


def sendAPICRequest(ip_addr, cookie, apicurl):
    url = 'http://'+ip_addr+apicurl
    http_header["Host"]=ip_addr
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.get(url,headers=http_header,cookies=cookies, timeout=60)
    return req.text

    


#################
#  MAIN MODULE  #
#################

if len(sys.argv) != 8:
    ip=raw_input("IP address of APIC? ")
    user=raw_input("Admin username? ")
    password=raw_input("Password? ")
    leafnum=raw_input("Leaf number [i.e. 101, 1103, etc.]? ")
    intf=raw_input("Interface [i.e. 1/1, 1/48, etc.]? ")
    metric=raw_input("What to monitor [i.e. pkts,cRCAlignErrors, octets, broadcastPkts, etc.]? ")
    interval=raw_input("Polling interval in seconds? ")
else:
    ip,user,password,leafnum,intf,metric,interval = sys.argv[1:]


switchport = intf.split('/')
baseDN='/api/node/mo/topology/pod-1/node-{}/sys/phys-[eth{}/{}]/dbgEtherStats.json?query-target=self'.format(leafnum,switchport[0],switchport[1])
print("Querying {}".format(baseDN))

cookie=getAPICCookie(ip, user, password)
if cookie:
    print("Cookie: {}\n".format(cookie))
    while True:
        r=sendAPICRequest(ip, cookie, baseDN)
        if r:
            parsed_json = json.loads(r)
	    parsedmetric = parsed_json['imdata'][0]['rmonEtherStats']['attributes'][metric]
	    print("\n{} = {}".format(metric, parsedmetric))
        else:
            print "That didn't work, we received no response back!"
	    sys.exit(1)
	time.sleep(1)

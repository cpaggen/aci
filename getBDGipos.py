#!/usr/bin/env python
#
# cpaggen; PoC-quality; quick and dirty script that does what I need
#
# queries APIC for all fvDB objects and finds bcastP attribute
#

import requests
import sys
import json
from pprint import pprint

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
    req = requests.get(url,headers=http_header,cookies=cookies)
    return req.text


def main():    
    if len(sys.argv) != 4:
        ip=raw_input("IP address of APIC? ")
        user=raw_input("Admin username? ")
        password=raw_input("Password? ")
    else:
        ip,user,password = sys.argv[1:]

    cookie=getAPICCookie(ip, user, password)
    if cookie:
        print "We have a cookie:\n  %s\n" % cookie
        apicurl='/api/node/class/fvBD.json'
	r=sendAPICRequest(ip, cookie, apicurl)
        if r:
            parsed_json = json.loads(r)
	    for bd in parsed_json['imdata']:
	        bdDN = bd['fvBD']['attributes']['dn']
	        bcastP = bd['fvBD']['attributes']['bcastP']
		print("{0} uses {1}").format(bdDN, bcastP)
        else:
            print "That didn't work, we received no response back!"
    else:
        print "Login error."


if __name__ == '__main__':
    sys.exit(main())




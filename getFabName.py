#!/usr/bin/env python
#
# no license, feel free to use this pretty poorly written code anywhere you see fit
# no warranty implied or expressed etc.
#

import requests
import sys
import json


def getAPICCookie(ip_addr, username, password):
    url = 'http://'+ip_addr+'/api/aaaLogin.xml'
    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (username, password)
    req = requests.post(url, data=xml_string, verify=False)
    rawcookie=req.cookies['APIC-cookie']
    return rawcookie


def sendAPICRequest(ip_addr, cookie, apicurl):
    url = 'http://'+ip_addr+apicurl
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.get(url, cookies=cookies)
    return req.text
    
def main(argv):
    if len(sys.argv) != 4:
        ip=raw_input("IP address of APIC? ")
        user=raw_input("Admin username? ")
        password=raw_input("Password? ")
    else:
        ip,user,password = sys.argv[1:]

    cookie=getAPICCookie(ip, user, password)
    apicurl='/api/node/class/infraCont.json'

    if cookie:
        print "We have a cookie:\n  %s\n" % cookie
        r=sendAPICRequest(ip, cookie, apicurl)
        if r:
            parsed_json = json.loads(r)
	    print "The name of your fabric is " + parsed_json['imdata'][0]['infraCont']['attributes']['fbDmNm']
        else:
            print "That didn't work, we received no response back!"

if __name__ == "__main__":
    main(sys.argv)

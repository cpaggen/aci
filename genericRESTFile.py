#!/usr/bin/env Python
#
# cpaggen
#
# no error checks - this is a very simple REST API 'poster' that pushes data to APIC
#

import requests
import sys

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


def sendAPICRequest(ip_addr, cookie, apicurl, data):
    url = 'http://'+ip_addr+apicurl
    http_header["Host"]=ip_addr
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.post(url,data=data,headers=http_header,cookies=cookies)
    return req.text

    


#################
#  MAIN MODULE  #
#################

if len(sys.argv) != 6:
    ip=raw_input("IP address of APIC? ")
    user=raw_input("Admin username? ")
    password=raw_input("Password? ")
    ffile=raw_input("File to use? ")
    apicurl=raw_input("URL to POST? ")
else:
    ip,user,password,ffile,apicurl = sys.argv[1:]

cookie=getAPICCookie(ip, user, password)
if cookie:
    print "We have a cookie:\n  %s\n" % cookie
    try:
        fp = open(ffile)
    except:
        print ("File error!")
	sys.exit(1)
    payload = fp.read()
    r=sendAPICRequest(ip, cookie, apicurl, payload)
    if r:
        print r
    else:
        print "That didn't work, we received no response back!"

#!/usr/bin/env Python
#
# cpaggen - verified with ACI 2.0; very likely to work with all versions
#
# Super simple script to retrieve all actions performed by a given userid
# I could use one generic function to query the API passing the URL
# For sake of clarity, I chose to break down the code in distinct functions
#
# to do: find actions for a given session ID
#   logged in sessions /api/node/class/aaaSessionLR.json? \
#     order-by=aaaSessionLR.created|desc
#     &query-target-filter=and(eq(aaaSessionLR.affected,"uni/userext/user-voxbone"), bw(aaaSessionLR.created,"2016-07-20T14:00:00","2016-07-20T15:00:00"))
#
#

import requests
import sys
import json
import pprint

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
    try:
        rawcookie=req.cookies['APIC-cookie']
    except:
        rawcookie=False
    return rawcookie


def sendAPICRequest(ip_addr, cookie, apicurl, data):
    url = 'http://'+ip_addr+apicurl
    http_header["Host"]=ip_addr
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.post(url,data=data,headers=http_header,cookies=cookies)
    return req.text

def verifyUser(ip_addr, cookie, apicurl):
    url = 'http://'+ip_addr+apicurl
    http_header["Host"]=ip_addr
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.get(url,headers=http_header,cookies=cookies)
    parsed_json = json.loads(req.text)
    userExists = int(parsed_json['totalCount'])
    # whether the user exists or not, the HTTP return code is 200 anyway
    # so you can't just rely on it to determine the existence of that user
    # however, totalCount's value is zero in case the user does not exist
    if userExists:
        return req
    else:
        return False

def getUserActionsLog(ip_addr, cookie, userid):
    relUrl = '/api/node/class/aaaModLR.json?query-target-filter=eq(aaaModLR.user,"%s")&order-by=aaaModLR.created|desc' % userid
    url = 'http://'+ip_addr+relUrl
    http_header["Host"] = ip_addr
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.get(url, headers=http_header, cookies=cookies)
    return req

#################
#  MAIN MODULE  #
#################

if len(sys.argv) != 5:
    ip=raw_input("IP address of APIC? ")
    user=raw_input("Admin username? ")
    password=raw_input("Password? ")
    userid=raw_input("User you want to query? ")
else:
    ip,user,password,userid = sys.argv[1:]

cookie=getAPICCookie(ip, user, password)
if cookie:
    print "We have a cookie:\n  %s\n" % cookie
    apicurl="/api/node/mo/uni/userext/user-%s.json" % userid
    print "Verifying that user userid %s exists (querying URL %s)" % (userid, apicurl)
    r=verifyUser(ip, cookie, apicurl)
    if r:
        lineSeparator = 120 * "="
        r=getUserActionsLog(ip, cookie, userid)
        parsed_json = json.loads(r.text)
        totalCount = int(parsed_json['totalCount'])
        print "Found %d log entries for user\n" % totalCount
        for aaaModLR in parsed_json['imdata']:
            print "Object: " + aaaModLR['aaaModLR']['attributes']['affected']
            print "Description: " + aaaModLR['aaaModLR']['attributes']['descr']
            print "Changeset: " + aaaModLR['aaaModLR']['attributes']['changeSet']
            print "Timestamp: " + aaaModLR['aaaModLR']['attributes']['created']
            print "Action: " + aaaModLR['aaaModLR']['attributes']['ind']
            print lineSeparator
    else:
        print "User not found. Please check that it exists within this list:\n"
        apicurl='/api/node/class/aaaUser.json'
        r=verifyUser(ip, cookie, apicurl)
        parsed_json=json.loads(r.text)
        for user in parsed_json['imdata']:
            print user['aaaUser']['attributes']['name']
else:
    print "Authentication failure or communication error. Is HTTP enabled on APIC?"


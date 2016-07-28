#!/usr/bin/env Python
#
# cpaggen
#
# super simple script to modify a tenant's description
# something I use to do a basic demo of ACI's programmability aspects
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

def verifyTenant(ip_addr, cookie, apicurl):
    url = 'http://'+ip_addr+apicurl
    http_header["Host"]=ip_addr
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.get(url,headers=http_header,cookies=cookies)
    parsed_json = json.loads(req.text)
    tenantExists = int(parsed_json['totalCount'])
    # if the tenant does not exist, the HTTP return code is 200 anyway
    # however, the totalCount json element's value is zero
    if tenantExists:
        return req
    else:
        return False


#################
#  MAIN MODULE  #
#################

if len(sys.argv) != 6:
    ip=raw_input("IP address of APIC? ")
    user=raw_input("Admin username? ")
    password=raw_input("Password? ")
    tenant=raw_input("Tenant's name? ")
    descr=raw_input("Description? ")
else:
    ip,user,password,tenant,descr = sys.argv[1:]

cookie=getAPICCookie(ip, user, password)
if cookie:
    print "We have a cookie:\n  %s\n" % cookie
    apicurl='/api/node/mo/uni/tn-%s.json' % tenant
    print "Verifying that tenant %s exists" % apicurl
    r=verifyTenant(ip, cookie, apicurl)
    if r:
        parsed_json=json.loads(r.text)
        curdescr=parsed_json['imdata'][0]['fvTenant']['attributes']['descr']
        print "Found tenant. Current description is set to %s" % curdescr
        tnurl='uni/tn-'+tenant
        payload='{"fvTenant":{"attributes":{"dn":"%s","descr":"%s"},"children":[]}}' % (tnurl,descr)
        r=sendAPICRequest(ip, cookie, apicurl, payload)
        print "Description changed. Verification ..."
        r=verifyTenant(ip, cookie, apicurl)
        parsedr=json.loads(r.text)
        pprint.pprint(parsedr)
    else:
        print "Tenant does not seem to exist. Please check that it exists within this list:\n"
        apicurl='/api/node/class/fvTenant.json'
        r=verifyTenant(ip, cookie, apicurl)
        parsed_json=json.loads(r.text)
        for tn in parsed_json['imdata']:
            print tn['fvTenant']['attributes']['dn']
else:
    print "Authentication failure or communication error. Is HTTP enabled on APIC?"


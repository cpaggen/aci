#!/usr/bin/env python
#
# ipost-light.py is a XML Jinja2 template rendering tool
# used to create large ACI configs and POST them to ACI
# in one shot. See README file for details.
#
# cpaggen July 2017 v1.0
#

import requests
from jinja2 import Template
import sys
import aci_credentials as aci
import jinja2
import re
import os

APIC_IP = aci.apic_ip_address
APIC_ADMIN = aci.apic_admin_user
APIC_ADMIN_PASS = aci.apic_admin_password
TEMPLATE_FILE = aci.template_file
TEMPLATE_PARAMS = aci.template_params

temp_params = {'tnPrefix': 'iPost-light', 'tnQuant': 10}

def getAPICCookie(ip_addr, username, password):
    url = 'http://'+ip_addr+'/api/aaaLogin.xml'

    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (username, password)
    req = requests.post(url, data=xml_string, verify=False)
    rawcookie=req.cookies['APIC-cookie']
    return rawcookie

def sendAPICRequest(ip_addr, cookie, apicurl, data):
    url = 'http://'+ip_addr+apicurl
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.post(url,data=data,cookies=cookies)
    return req.text

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

def getRESTUrl(filename):
    with open(filename) as myfile:
        secondLine=myfile.readlines()[1:2]
        match = re.search('<!-- (.*) -->', str(secondLine))
        if not match:
            raise ParseError('ERROR: Unable to locate REST URL in XML template')
        url = match.group(1)
        print("##DEBUG## URL we are posting to is {}".format(url))
        return url

def main():
    url = getRESTUrl(TEMPLATE_FILE)
    cookie=getAPICCookie(APIC_IP, APIC_ADMIN, APIC_ADMIN_PASS)
    if cookie:
        print("##DEBUG## APIC cookie is {}".format(cookie))
        print("##DEBUG## Template params are {}".format(TEMPLATE_PARAMS))
        result = render(TEMPLATE_FILE, eval(TEMPLATE_PARAMS))
        print("##DEBUG## Rendered templated is {}".format(result))
        r=sendAPICRequest(APIC_IP, cookie, url, result)
        if r:
            print r
        else:
            print "That didn't work, we received no response back!"

if __name__ == "__main__":
    sys.exit(main())



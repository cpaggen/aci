#!/usr/bin/env python
#
# ipost-light.py is a XML Jinja2 template rendering tool
# used to create large ACI configs and POST them to ACI
# in one shot. See README file for details.
#
# code quality is proof-of-concept (tested/verified on CentOS 7.x and Windows 7)
# validated against ACI 2.3(1) release
#
# cpaggen July 2017 v1.0
#
# 
# MIT License
#
# Copyright (c) 2017 Christophe Paggen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import requests
from jinja2 import Template
import sys
import aci_credentials as aci
import jinja2
import re
import os
import requests.packages.urllib3
import json

# Classic hack to disable cert validation warnings
# use only if you really, really trust the remote server
requests.packages.urllib3.disable_warnings()

APIC_IP = aci.apic_ip_address
APIC_ADMIN = aci.apic_admin_user
APIC_ADMIN_PASS = aci.apic_admin_password    
TEMPLATE_FILE = aci.template_file            # XML template filename
TEMPLATE_PARAMS = aci.template_params        # a dictionary of key/value pairs


def getAPICCookie(ip_addr, username, password):
    url = 'https://'+ip_addr+'/api/aaaLogin.xml'

    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (username, password)
    req = requests.post(url, data=xml_string, verify=False)
    try:
        rawcookie=req.cookies['APIC-cookie']
    except KeyError:
        rawcookie=''
    return rawcookie

def sendAPICRequest(ip_addr, cookie, apicurl, data):
    url = 'https://'+ip_addr+apicurl
    cookies = {}
    cookies['APIC-cookie'] = cookie
    req = requests.post(url,data=data,cookies=cookies, verify=False)
    return req.text

def renderTemplate(template, params):
    path, filename = os.path.split(template)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(params)

def getRESTUrl(filename):
    with open(filename) as myfile:
        secondLine=myfile.readlines()[1:2]
        match = re.search('<!-- (.*) -->', str(secondLine))
        if not match:
            raise Exception('ERROR: Unable to locate REST URL in XML template')
        url = match.group(1)
        print("##DEBUG## URL we are posting to is {}".format(url))
        return url

def main():
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
        print("##DEBUG## Parameters detected via command line: {}".format(params))
        TEMPLATE_PARAMS=json.dumps(params)
    else:
        TEMPLATE_PARAMS=aci.template_params

    url = getRESTUrl(TEMPLATE_FILE)
    cookie=getAPICCookie(APIC_IP, APIC_ADMIN, APIC_ADMIN_PASS)
    if cookie:
        print("##DEBUG## APIC cookie is {}".format(cookie))
        print("##DEBUG## Template params are {}".format(TEMPLATE_PARAMS))
        result = renderTemplate(TEMPLATE_FILE, eval(TEMPLATE_PARAMS))
        print("##DEBUG## Rendered templated is {}".format(result))
        r=sendAPICRequest(APIC_IP, cookie, url, result)
        if r:
            print("##DEBUG## All done - result is {}".format(r))
        else:
            raise Exception('ERROR: POST to APIC failed')
    else:
        raise Exception('ERROR: Failed to log into APIC')

if __name__ == "__main__":
    sys.exit(main())



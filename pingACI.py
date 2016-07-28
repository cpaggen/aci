#!/usr/bin/env Python
#

import requests
import sys

def getAPICCookie(ip_addr, username, password, usetls):
    protocol='http'
    if usetls:
        protocol='https'
    url = protocol+'://'+ip_addr+'/api/aaaLogin.xml'
    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (username, password)
    req = requests.post(url, data=xml_string, verify=False)
    rawcookie=req.cookies['APIC-cookie']
    return rawcookie

if __name__ == '__main__':
    if len(sys.argv) != 5:
        ip=raw_input("IP address of APIC? ")
        user=raw_input("Admin username? ")
        password=raw_input("Password? ")
        usetls=raw_input("Use TLS? [y/n] ")
    else:
        ip,user,password,usetls = sys.argv[1:]

    if usetls=='y':
        usetls=True
    else:
        usetls=False

    print("User {} logging into APIC {} (TLS: {})".format(user, ip, usetls))

    cookie=getAPICCookie(ip, user, password, usetls)
    if cookie:
        print("Obtained cookie: {}\n".format(cookie))
        print("APIC is alive.")
    else:
        print "That didn't work, we received no response back!"
        sys.exit(1)

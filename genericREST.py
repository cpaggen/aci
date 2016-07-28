#!/usr/bin/env Python
#
# cpaggen

import urllib2
import base64
import sys

handlers = []
hh = urllib2.HTTPHandler()
hh.set_http_debuglevel(0)
handlers.append(hh)

http_header={"User-Agent" : "Chrome/17.0.963.46",
             "Accept" : "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,text/png,*/*;q=0.5",
             "Accept-Language" : "en-us,en;q=0.5",
             "Accept-Charset" : "ISO-8859-1",
             "Content-type": "application/x-www-form-urlencoded"
            }

def createAuthHeader(username,password):
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    return ('Basic %s' % base64string)

def getAPICCookie(ip_addr, authheader, username, password):
    url = 'http://'+ip_addr+'/api/aaaLogin.xml'

    # create 'opener' (OpenerDirector instance)
    opener = urllib2.build_opener(*handlers)
    # Install the opener.
    # Now all calls to urllib2.urlopen use our opener.
    urllib2.install_opener(opener)

    http_header["Host"]=ip_addr
    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (username, password)
    req = urllib2.Request(url=url, data=xml_string, headers=http_header)

    try:
      response = urllib2.urlopen(req)
    except urllib2.URLError, e:
      print 'Failed to obtain auth cookie: %s' % (e)
      return 0
    else:
      rawcookie=response.info().getheaders('Set-Cookie')
      return rawcookie[0]


def sendAPICRequest(ip_addr, cookie, url):
    url = 'https://'+ip_addr+url
    opener = urllib2.build_opener(*handlers)
    urllib2.install_opener(opener)
    http_header["Host"]=ip_addr
    http_header["Cookie"]=cookie

    req = urllib2.Request(url=url,headers=http_header)

    try:
     response = urllib2.urlopen(req)
    except urllib2.URLError, e:
     print "URLLIB2 error:\n  %s\n  URL: %s\n  Reason: %s" % (e, e.url, e.reason)
    else:
     return response

    


#################
#  MAIN MODULE  #
#################

if len(sys.argv) != 5:
    ip = raw_input("IP: ")
    user = raw_input("username: ")
    password = raw_input("password: ")
    url = raw_input("URL: ")
else:
    ip, user, password, url = sys.argv[1:]

basicauth=createAuthHeader(user, password)
cookie=getAPICCookie(ip, basicauth, user, password)
if cookie:
    print "We have a cookie:\n  %s\n" % cookie

    r=sendAPICRequest(ip, cookie, url)
    results = r.read()
    print results
    fp = open("genericREST-script_results.xml", "w")
    fp.write(results)
    fp.close()
    print 
    "\t ... done! Output written to genericREST-script_results.xml"

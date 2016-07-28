# Validated with FCS release
# author: cpaggen
# quality: PoC-level, no error checks

import cobra.mit.access
import cobra.mit.session
import os
from cobra.model.aaa import User, UserDomain, UserRole
from cobra.mit.request import ConfigRequest


os.path.abspath("C:/Users/cpaggen/PycharmProjects/COBRA_101")
print('Reading user names from file ...')
with open("apicusers.txt") as fp:
     users = fp.readlines()

APIC = raw_input("IP of APIC: ")
USER = raw_input("Username: ")
PASS = raw_input("Password: ")
url = "https://" + APIC
print('Logging into APIC ...')
ls = cobra.mit.session.LoginSession(url, USER, PASS, secure=False, timeout=180)
moDir = cobra.mit.access.MoDirectory(ls)
moDir.login()

for user in users:
    # to create podx users, list comprehension users=['pod'+str(x) for x in range(1,10)] works well
    user = user.lower().rstrip()
    print("Processing user %r") % user
    aaaUserExt = moDir.lookupByDn('uni/userext')
    aaaUser = User(aaaUserExt,user)
    aaaUser.email = user + '@cisco.com'
    aaaUser.descr = 'Created by the Cobra SDK'
    aaaUser.firstName = user[0].capitalize() + '.'
    aaaUser.lastName = user[1].capitalize() + user[2:]
    aaaUser.pwd = 'cisco'
    aaaUserDomain = UserDomain(aaaUser,'all')
    aaaUserRole = UserRole(aaaUserDomain,'admin')
    aaaUserRole.privType = 'writePriv'
    cfg = ConfigRequest()
    #cfg.addMo(aaaUserExt)
    cfg.addMo(aaaUserExt)
    moDir.commit(cfg)
    print("\t...done")

print("All users processed.\n")


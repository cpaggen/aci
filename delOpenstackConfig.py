__author__ = 'cpaggen'

#
# deletes all tenants on APIC
# no warning, brutal!
#
# cpaggen

import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.fv
import sys

def apicLogin(ip, username, password):
    # log into an APIC and create a directory object
    url = "https://" + ip
    print('Logging into APIC ...')
    ls = cobra.mit.session.LoginSession(url, username, password, secure=False, timeout=180)
    moDir = cobra.mit.access.MoDirectory(ls)
    try:
        moDir.login()
    except:
        print("Login error (wrong username or password?)")
        exit(1)
    return moDir

def printNames(moDir):
    for x in moDir:
        try:
            if x.name:
                print "\t\t{}".format(x.name)
            else:
                print "\t\t{}".format(x)
        except AttributeError:
            continue

def deleteMo(moDir, moClass, prefix):
    usersToKeep = ['admin']
    print "Looking for existing {} ...".format(moClass)
    mo = moDir.lookupByClass(moClass)
    print " --> found {}".format(len(mo))
    printNames(mo)
    for obj in mo:
        objMo = moDir.lookupByDn(obj.dn)
	if obj.name.find(prefix) >= 0 or obj.name.startswith("bundle"): 
            print("\t\t deleting {}".format(obj.dn))
	    objMo.delete()
            c = cobra.mit.request.ConfigRequest()
            c.addMo(objMo)
            moDir.commit(c)
            print "\t\t\t--> deleted {}!".format(obj.dn)


def main(ip, username, password, prefix):
    moDir = apicLogin(ip, username, password)
    moList = ['fvTenant', 'infraAttEntityP', 'fvnsVlanInstP', 'physDomP', 'l2extDomP', 'l3extDomP', 'infraAccPortGrp', 'infraAccPortP', \
    'infraNodeP', 'infraAccBndlGrp', 'infraAccBndlPolGrp', 'infraHPathS', 'fabricHIfPol', 'infraHPortS', 'cdpIfPol', 'lldpIfPol', 'lacpLagPol', 'lacpLagPol', 'fabricExplicitGEp', \
    'infraAccNodePGrp', 'vpcInstPol', 'vmmDomP' ]
    for mo in moList:
        deleteMo(moDir, mo, prefix)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        ip = raw_input("IP: ")
        username = raw_input("username: ")
        password = raw_input("password: ")
	prefix = raw_input("prefix marked for deletion: ")
    else:
        ip, username, password, prefix = sys.argv[1:]

    main(ip, username, password, prefix)

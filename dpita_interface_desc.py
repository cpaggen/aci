#
# Code written entirely by Daniel Pita (dpita at cisco dot com)
# 
import requests
import json
import collections
import getpass
import urllib3
import shutil
import csv
from collections import defaultdict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APIC_URL = ""
APIC_USER = ""
APIC_PASS = ""
ROW = {}

master = defaultdict(list)
master2 = {}
neigh_int_str = ""
node_idn = ""

neigh_int = ""
neigh_uint = ""
neigh_cdp_dn = []
neigh_name = []
infra_acc = {}
inner_acc = {}
node_id = ""
test2 = ""
e_id = ""


def login(apic_url=APIC_URL, apic_user=APIC_USER, apic_pass=APIC_PASS):
    '''
    Logs into the specified APIC with given credentials.
    Will log into Fab1 by default.

    Returns: Session Object, so we don't have to keep passing cookies.

    '''
    login_url = "https://" + apic_url + "/api/aaaLogin.json"
    payload = {"aaaUser": {"attributes": {"name": apic_user, "pwd": apic_pass}}}
    s = requests.Session()
    s.post(login_url, data=json.dumps(payload), verify=False)
    return s


def main():
    '''
       APIC_URL = input("Enter APIC IP: ")
       APIC_USER = input("Enter username: ")
       APIC_PASS = getpass.getpass("Enter password: ", stream=None)
       '''

    APIC_URL = "10.1.1.10"
    APIC_USER = "admin"
    APIC_PASS = "password"

    session = login(APIC_URL, APIC_USER, APIC_PASS)

    neigh_int_str = ""
    node_idn = ""
    row_dict = {}
    row = {}
    row_num = 0
    row_dict = {}
    lldp_dict = {}
    lldp_row = {}

    lldp_resp = session.get("https://" + APIC_URL + '/api/node/class/lldpAdjEp.json')
    lldp_friends = json.loads(lldp_resp.text)['imdata']
    accHportS_resp = session.get("https://" + APIC_URL + '/api/node/class/infraHPortS.json')
    accHportS_friends = json.loads(accHportS_resp.text)['imdata']

    portBlk_resp = session.get("https://" + APIC_URL + '/api/node/class/infraPortBlk.json')
    portBlk_friends = json.loads(portBlk_resp.text)['imdata']

    # print(lldp_resp)
    # print(lldp_friends)

    for i in portBlk_friends:
        # print(portBlk_friends, json.dumps(i, indent=4, sort_keys=True))
        infra_port_dn = (i["infraPortBlk"]["attributes"]["dn"])
        # print(infra_port_dn)
        # print("dn = ", infra_port_dn)
        dn_split = infra_port_dn.split('/')
        # print(dn_split)

        accport = dn_split[2].split('-')[1]
        node = accport.split('_')[0]
        hports = dn_split[3]
        portblk = dn_split[4]
        accInt = hports.split('-')[1]
        fromCard = i["infraPortBlk"]["attributes"]["fromCard"]
        fromPort = i["infraPortBlk"]["attributes"]["fromPort"]
        toPort = i["infraPortBlk"]["attributes"]["toPort"]


        print(accport, hports, portblk)
        if fromPort == toPort:
            print('member ints', fromCard,'/',fromPort)
        elif fromPort < toPort:
            for num in range (int(fromPort), int(toPort) + 1):
                print('range ints', fromCard, '/', num)

        new_accInt = r_intmod(accInt)

        print('building lldp dn query ',node, new_accInt)



        lldp_resp1 = session.get(
            "https://" + APIC_URL + '/api/node/mo/topology/pod-1/node-' + node + '/sys/lldp/inst/if-[' + new_accInt + ']/adj-1.json?query-target=self')
        lldp_friends1 = json.loads(lldp_resp1.text)['imdata']
        cdp_resp1 = session.get(
            "https://" + APIC_URL + '/api/node/mo/topology/pod-1/node-' + node + '/sys/cdp/inst/if-[' + new_accInt + ']/adj-1.json?query-target=self')
        cdp_friends1 = json.loads(cdp_resp1.text)['imdata']

        # print('lldp resp code', lldp_resp.status_code)
        # print('lldp resp count', json.loads(lldp_resp1.text)['totalCount'])

        # print('cdp resp code', cdp_resp1.status_code)
        # print('cdp resp count', json.loads(cdp_resp1.text)['totalCount'])

        # print(type(lldp_resp1))

        if lldp_resp1.status_code == 200 and json.loads(lldp_resp1.text)['totalCount'] != "0":
            for i in lldp_friends1:
                # print('lldp friends2 =', json.dumps(i, indent=4, sort_keys=True))

                '''isolate node ID from dn in format "node-###" '''
                node_id = (i["lldpAdjEp"]["attributes"]["dn"]).split('/')
                node_id = node_id[2]
                # print(node_id.split('-'))
                node_id = node_id.split('-')
                node_idn = node_id[1]
                # print(node_idn)

                '''isolate interface from dn in format "eth1/##" '''
                neigh_int = (i["lldpAdjEp"]["attributes"]["dn"]).split('[')
                neigh_int = neigh_int[1].split(']')
                # print(neigh_int)
                # neigh_uint = neigh_int[0].replace('/', '_')
                # neigh_uint = neigh_uint.replace('eth', 'E')
                # print(neigh_int[0])
                neigh_int_str = neigh_int[0]
                # print(neigh_int_str)

                neigh_name = (i["lldpAdjEp"]["attributes"]["sysName"])
                # print(neigh_name)

                lldp_dict.update(
                    {'node': node_idn, 'int': neigh_int_str, 'neigh': neigh_name, 'infraPortBlk_dn': infra_port_dn})
                lldp_row.update({row_num: lldp_dict})
                row_num = row_num + 1
                lldp_dict = {}

        elif cdp_resp1.status_code == 200 and json.loads(cdp_resp1.text)['totalCount'] != "0":
            # print('ELSE IF')
            for i in cdp_friends1:
                # print('cdp friends2 =', json.dumps(i, indent=4, sort_keys=True))

                '''isolate node ID from dn in format "node-###" '''
                node_id = (i["cdpAdjEp"]["attributes"]["dn"]).split('/')
                node_id = node_id[2]
                # print(node_id.split('-'))
                node_id = node_id.split('-')
                node_idn = node_id[1]
                # print('cdp',node_idn)

                '''isolate interface from dn in format "eth1/##" '''
                neigh_int = (i["cdpAdjEp"]["attributes"]["dn"]).split('[')
                neigh_int = neigh_int[1].split(']')
                # print(neigh_int)
                # neigh_uint = neigh_int[0].replace('/', '_')
                # neigh_uint = neigh_uint.replace('eth', 'E')
                # print(neigh_int[0])
                neigh_int_str = neigh_int[0]
                # print('cdp',neigh_int_str)

                neigh_name = (i["cdpAdjEp"]["attributes"]["sysName"])
                # print('cdp',neigh_name)

                lldp_dict.update(
                    {'node': node_idn, 'int': neigh_int_str, 'neigh': neigh_name, 'infraPortBlk_dn': infra_port_dn})
                lldp_row.update({row_num: lldp_dict})
                row_num = row_num + 1
                lldp_dict = {}

        else:
            print('http 400')

    for i in accHportS_friends:
        infra_h_dn = (i["infraHPortS"]["attributes"]["dn"])
        # print('im a dn = ', infra_h_dn)
        hports = intmod(neigh_int_str)
        # print('im a replica = ', 'uni/infra/accportprof-' + node_idn + '_IntProf/hports-' + hports + '-typ-range')
        # custom_dn = 'uni/infra/accportprof-' + node_idn + '_IntProf/hports-' + hports + '-typ-range'
        # print(custom_dn)
        # print(hports)

    print('row ', lldp_row)



    #post(lldp_row, APIC_URL, APIC_USER, APIC_PASS)


def post(desc_dict, apic_url=APIC_URL, apic_user=APIC_USER, apic_pass=APIC_PASS):
    '''
    Logs into the specified APIC with given credentials.
    Will log into Fab1 by default.

    its a post....maybe?

    '''

    login_url = "https://" + apic_url + "/api/aaaLogin.json"
    payload = {"aaaUser": {"attributes": {"name": apic_user, "pwd": apic_pass}}}
    s = requests.Session()
    s.post(login_url, data=json.dumps(payload), verify=False)

    post_url = "https://" + apic_url + "/api/mo/uni.json"

    for key in desc_dict:
        #print(key)

        body = {
            "infraPortBlk": {
                "attributes": {
                    "dn": desc_dict[key]['infraPortBlk_dn'],
                    "descr": desc_dict[key]['neigh']
                },
                "children": []
            }
        }

        post = s.post(post_url, data=json.dumps(body), verify=False)
        #print(post.status_code)


def intmod(master):
    # print(master)
    mod_master1 = master.replace('/', '_')
    mod_master1 = mod_master1.replace('eth', 'E')
    # print(mod_master1)
    return mod_master1


def r_intmod(master):
    # print(master)
    mod_master1 = master.replace('_', '/')
    mod_master1 = mod_master1.replace('E', 'eth')
    # print(mod_master1)
    return mod_master1


if __name__ == "__main__":
    main()

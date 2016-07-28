from __future__ import print_function
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import atexit
import sys

def GetObj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break
    return obj

def main():
    if len(sys.argv) != 3:
        print("Usage: infectVM.py <VM_name> <infected_state>")
        sys.exit(1)

    vmName, infectedVal = sys.argv[1:]
    serviceInstance = SmartConnect(host="10.48.58.109",
                                   user="root",
                                   pwd="",
                                   port=443)

    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()
    customFieldMgr = content.customFieldsManager
    fields = (obj.name for obj in customFieldMgr.field)
    if "Infected" in fields:
        print("Found custom attribute 'Infected' in attributes")
    else:
        print("Adding custom field 'Infected'")
        customFieldMgr.AddCustomFieldDef(name = "Infected", moType = vim.VirtualMachine)

    print("Looking for {} in vCenter inventory - this may take a few seconds ...".format(vmName))
    vm = GetObj(content, [vim.VirtualMachine], vmName)
    if vm:
        print ("\tfound {0}\n\tsetting value of 'Infected' to {1}".format(vm.name,infectedVal))
        vm.setCustomValue(key="Infected", value=infectedVal)
        print("\tdone.")
    else:
        print("\tVM not found in vCenter inventory.")

# Main section
if __name__ == "__main__":
    sys.exit(main())


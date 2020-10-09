#!/home/slaviole/Projects/cliTools/venv/bin/python

from ncclient import manager
import untangle
import argparse
import yaml


def view_clsfr(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for Classifer tags.
        No return value.
    '''
    try:
        for clsfr in obj.rpc_reply.data.classifiers.classifier:
            print('')
            print("Classifier Name:     ", clsfr.name.cdata)
            print("  filter-parameter:  ", clsfr.filter_entry.filter_parameter.cdata)
            print("  logical-not:       ", clsfr.filter_entry.logical_not.cdata)
            try:
                print("    Outer Tag Level: ", clsfr.filter_entry.vtags.tag.cdata)
                print("    VLAN ID:         ", clsfr.filter_entry.vtags.vlan_id.cdata)
            except:
                pass
            try:
                print("    Untagged-excl-pri-tagged: ",clsfr.filter_entry.untagged_exclude_priority_tagged.cdata)
            except:
                pass
    except:
        print("No Classifiers found.")


def view_sfs(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for sfs(i.e. vnf) tags.
        No return value.
    '''
    try:
        line = 30 * "*"
        num_sfs = len(obj.rpc_reply.data.sfs)
        for item in obj.rpc_reply.data.sfs.sf:
            print("")
            print("")
            print(item.sf_name.cdata)
            print(line)
            print("CPUs Assigned: ", item.sf_state.num_cpus.cdata)
            print("Mem Allocated: ", item.sf_state.mem_allocated.cdata)
            print("Admin State:   ", item.sf_operation.state.cdata)
            print("Operational State:   ", item.sf_state.oper_state.cdata)
            print("VNC Console:   ", item.sf_state.console.vnc_port.cdata)
            num_if = len(item.sfo.network_interface)
            for intf in item.sfo.network_interface:
                print(line)
                if_name = intf.name.cdata
                if_type = intf.network_type.cdata
                print(if_name)
                print("Interface Type: ",if_type)
                if not if_type == "default":
                    log_port = intf.logical_port.cdata
                    print("Logical Port: ", log_port)
            print(line)
    except:
        print("No SFs found.")


def view_sffs(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for sffs(i.e. service chains) tags.
        No return value.
    '''
    try:
        for fd in obj.rpc_reply.data.sffs.sff:
            print()
            print('SFF Name: ', fd.sff_name.cdata)
            print('SFF Mode:', fd.sff_mode.cdata)
            for fp in fd.interface:
                print('  ', 'Flow Point Name: ', fp.name.cdata)
                print('    ', 'Logical Port: ', fp.logical_port.cdata)
                for clsfr in fp.classifier_list:
                    print('    ', 'Classifier: ', clsfr.cdata)
    except:
        print("No SFFs found")


def get_ansible_logindata(fn):
    ''' Takes an ansible-playbook filename as input, extracts the server name from the file,
        uses that server name to look up the ip, user, and pwd from the ansible hosts file.
        Returns a dict with the ip, user, and pwd.
    '''
    with open(fn) as f:
        ymlmap = yaml.safe_load(f)
        server = ymlmap['server']
    with open('hosts') as f:
        f.seek(0)
        while True:
            line = f.readline()
            lst = line.split()
            if lst[0] == server:
                ip_lst = lst[1].split("=")
                ip = ip_lst[1]
                user_lst = lst[2].split("=")
                user = user_lst[1]
                pwd_lst = lst[3].split("=")
                pwd = pwd_lst[1]
                break
    ansible_logindata = {'ip': ip, 'user': user, 'pwd': pwd}
    return ansible_logindata


def get_nc_obj(nc_creds):
    ''' Takes D-NFVI server login credentials, makes a Netconf get for all config and oper data.
        Returns an Untangle object with the parsed xml tree.
    '''
    with manager.connect(host=nc_creds['ip'],
                             port=830,
                             username=nc_creds['user'],
                             password=nc_creds['pwd'],
                             hostkey_verify=False,
                             allow_agent=False,
                             look_for_keys=False
                             ) as netconf_manager:

        data = netconf_manager.get()
    data_str = str(data)
    d_obj = untangle.parse(data_str)
    return d_obj


def main():
    ''' Parses command line argument for ansible playbook filename and D-NFVI tag to view.
        Calls ansible_login_data to get credentials. Uses those credentials to call get_nc_obj
        and return an untangle tree object that is easily parses.
        Based on arg.option calls the appropriate function to display the D-NFVI tag.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Provide an ansible-playbook filename to get device credentials")
    parser.add_argument("option", help="Provide view option ( one of clsfr,sfs,sffs)")
    args = parser.parse_args()
    if args.option != 'sfs' and args.option != 'sffs' and args.option != 'clsfr':
        print("Incorrect 2nd argument. Must be one of sfs, sffs, clsfr")
        return

    creds = get_ansible_logindata(args.filename)

    dnfvi_obj = get_nc_obj(creds)

    if args.option == 'clsfr':
        print("Searching for Classifiers")
        view_clsfr(dnfvi_obj)
    elif args.option == 'sfs':
        print("Searching for VNF's/SF's")
        view_sfs(dnfvi_obj)
    else:
        print("Searching SFF's (Service Chain build)")
        view_sffs(dnfvi_obj)


if __name__ == "__main__":
    main()



from ncclient import manager
import requests
import untangle
import click
#import yaml



def get_nc_obj(nc_creds, filter):
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

        data = netconf_manager.get(filter)
    data_str = str(data)
    d_obj = untangle.parse(data_str)
    return d_obj

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

def view_fds(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for fds(i.e. Forwarding Domains) tags.
        No return value.
    '''
    try:
        for item in obj.rpc_reply.data.fds.fd:
            print()
            print('FD Name: ', item.name.cdata)
            print('FD Mode:', item.mode.cdata)
  
    except:
        print("No FDs found")

def view_fps(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for fds(i.e. Forwarding Domains) tags.
        No return value.
    '''
    try:
        for item in obj.rpc_reply.data.fps.fp:
            print()
            print('Fp Name: ', item.name.cdata)
            print('FD Name: ', item.fd_name.cdata)
            print('Logical Port: ', item.logical_port.cdata)
  
    except:
        print("No FPs found")

def view_interfaces(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for Interfaces(i.e. Forwarding Domains) tags.
        No return value.
    '''
    try:
        for item in obj.rpc_reply.data.interfaces.interface:
            print()
            print('Interface Name: ', item.name.cdata)
           # print('IP Address: ', item.ipv4.addresses.ip.cdata)
  
    except:
        print("No Interfaces found")

classifiers_filter = '''
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
        <classifiers xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-mef-classifier">
        <classifier>
        </classifier>
        </classifiers>
    </filter>
    '''

sffs_filter = '''
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
        <sffs xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-sfc">
            <sff>
            </sff>
        </sffs>
    </filter>
    '''

sfs_filter = '''
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
        <sfs xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-sf">
            <sf>
            </sf>
        </sfs>
    </filter>
    '''


fds_filter = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
          <fds xmlns="urn:ciena:params:xml:ns:yang:ciena-pn:ciena-mef-fd">
            <fd>
            </fd>
          </fds>
        </filter>
    '''

fps_filter = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
          <fps xmlns="urn:ciena:params:xml:ns:yang:ciena-pn:ciena-mef-fp">
            <fp>
            </fp>
          </fps>
        </filter>
    '''

interfaces_filter = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
          <interfaces xmlns="http://openconfig.net/yang/interfaces">
            <interface>
            </interface>
          </interfaces>
        </filter>
    '''




creds = {'ip': '10.181.34.2', 'user': 'user', 'pwd': 'ciena123'}

@click.group()
def cli():
    pass

@cli.group()
def show():
    pass

@show.command()
def classifiers():
    dnfvi_obj = get_nc_obj(creds, classifiers_filter)
    view_clsfr(dnfvi_obj)

@show.command()
def sffs():
    dnfvi_obj = get_nc_obj(creds, sffs_filter)
    view_sffs(dnfvi_obj)

@show.command()
def sfs():
    dnfvi_obj = get_nc_obj(creds, sfs_filter)
    view_sfs(dnfvi_obj)

@show.command()
def fds():
    dnfvi_obj = get_nc_obj(creds, fds_filter)
    view_fds(dnfvi_obj)

@show.command()
def fps():
    dnfvi_obj = get_nc_obj(creds, fps_filter)
    view_fps(dnfvi_obj)

@show.command()
def interfaces():
    dnfvi_obj = get_nc_obj(creds, interfaces_filter)
    view_interfaces(dnfvi_obj)

#if __name__ == "__main__":
#    cli()




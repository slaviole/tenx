import os
from ncclient import manager
from ncclient.xml_ import to_ele
import requests
import untangle
import click
from jinja2 import Template
from prettytable import PrettyTable


def get_nc_obj(nc_creds, filter):
    ''' Takes D-NFVI server login credentials, makes a Netconf get for all config and oper data.
        Returns an Untangle object with the parsed xml tree.
    '''

    ''' node = os.environ.get('NODE')
    print("Node is " + str(node))
    nc_creds['ip'] = os.getenv('NODE')
    print("NC_CREDS dict are " + str(nc_creds))'''
    file = open("/home/slaviole/activenode.txt", "r")
    if file.mode == 'r':
        activenode = file.read()
    else:
        activenode = "3906_1"
    nc_creds['ip'] = nodes[activenode]
    print()
    print(f"[{activenode}]")
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

def edit_nc_obj(nc_creds, template):
    ''' Takes D-NFVI server login credentials, makes a Netconf get for all config and oper data.
        Returns an Untangle object with the parsed xml tree.
    '''
    file = open("/home/slaviole/activenode.txt", "r")
    if file.mode == 'r':
        activenode = file.read()
    else:
        activenode = "3906_1"
    nc_creds['ip'] = nodes[activenode]
    print()
    print(f"[{activenode}]")
    with manager.connect(host=nc_creds['ip'],
                             port=830,
                             username=nc_creds['user'],
                             password=nc_creds['pwd'],
                             hostkey_verify=False,
                             allow_agent=False,
                             look_for_keys=False
                             ) as netconf_manager:

        data = netconf_manager.edit_config(target='running', config=template)
    data_str = str(data)
    d_obj = untangle.parse(data_str)
    return d_obj

def send_rpc(nc_creds, template):
    ''' Sends an RPC message
    '''
    file = open("/home/slaviole/activenode.txt", "r")
    if file.mode == 'r':
        activenode = file.read()
    else:
        activenode = "3906_1"
    nc_creds['ip'] = nodes[activenode]
    print()
    print(f"[{activenode}]")
    with manager.connect(host=nc_creds['ip'],
                             port=830,
                             username=nc_creds['user'],
                             password=nc_creds['pwd'],
                             hostkey_verify=False,
                             allow_agent=False,
                             look_for_keys=False
                             ) as netconf_manager:

        data = netconf_manager.dispatch(to_ele(template))
    data_str = str(data)
    print(data_str)
    d_obj = untangle.parse(data_str)
    return d_obj


def view_clsfr(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for Classifer tags.
        No return value.
    '''
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
    '''

    x = PrettyTable()
    x.field_names = ["Name", "VlanID/Untagged"]
    x.align["Name"] = "l"

    try:
        for clsfr in obj.rpc_reply.data.classifiers.classifier:
            try:
                if (clsfr.filter_entry.untagged_exclude_priority_tagged.cdata):
                    vlanid_untagged = "Untagged"
            except:
                vlanid_untagged = clsfr.filter_entry.vtags.vlan_id.cdata

            x.add_row([clsfr.name.cdata, vlanid_untagged])
    except:
        print("No Classifiers found.")
    print(x)








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
            print('FP Name: ', item.name.cdata)
            print('FD Name: ', item.fd_name.cdata)
            print('Logical Port: ', item.logical_port.cdata)

    except:
        print("No FPs found")

def view_interfaces(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for Interfaces(i.e. Forwarding Domains) tags.
        No return value.
    '''
    x = PrettyTable()
    x.field_names = ["Interface", "IP Address", "Operational Status"]
    x.align["Interface"] = "l"
    x.align["IP Address"] = "l"
    try:
        for item in obj.rpc_reply.data.interfaces.interface:
            if (len(item.name.cdata) > 2) and ((item.name.cdata) != "remote"):
                fullIp = item.ipv4.addresses.address.config.ip.cdata + "/" + item.ipv4.addresses.address.config.prefix_length.cdata
                x.add_row([item.name.cdata, fullIp, item.state.oper_status.cdata])
    except:
        print("No Interfaces found")
    print(x)

def view_sr(obj):
    ''' Takes an Untangle Object as Input, parses it, and prints out Field names and values
        of interest for Segment-Routing tags.
        No return value.
    '''
    print("TESTING*****: ", obj.rpc_reply.data.segment_routing.srgb.lower_bound.cdata)
    #    try:
    for item in obj.rpc_reply.data.segment_routing.connected_prefix_sid_map:
        print()
        print('Prefix: ', item.prefix.cdata)
        print('Prefix: ', item.prefix.cdata)
        print('Interfaces: ', item.interface.cdata)
        # print('IP Address: ', item.ipv4.addresses.ip.cdata)
#    except:
#        print("No prefixes found")


classifiers_filter = '''
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
        <classifiers xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-mef-classifier">
        <classifier>
        </classifier>
        </classifiers>
    </filter>
    '''

editClassifiers = Template('''
    <config>
        <classifiers>
        {% if vlanid=='untagged'  %}
            <classifier operation="{{operation}}">
            <name>Untagged</name>
            <filter-entry>
                <filter-parameter xmlns:classifier="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-mef-classifier">classifier:vtag-stack</filter-parameter>
                <logical-not>false</logical-not>
                <untagged-exclude-priority-tagged>true</untagged-exclude-priority-tagged>
            </filter-entry>
            </classifier>
        {% else %}
            <classifier operation="{{operation}}">
            <name>VLAN{{vlanid}}</name>
            <filter-entry>
                <filter-parameter xmlns:classifier="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-mef-classifier">classifier:vtag-stack</filter-parameter>
                <logical-not>false</logical-not>
                <vtags>
                <tag>1</tag>
                <vlan-id>{{vlanid}}</vlan-id>
                </vtags>
            </filter-entry>
            </classifier>
        {% endif %}
        </classifiers>
    </config>
    ''')

editSffs = Template('''
    <config>
        <sffs xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-sfc">
            <sff operation="{{operation}}">
            <sff-name>SFFS-{{ vlanid }}</sff-name>
            {% if operation == "replace" %}
                <sff-mode>{{mode}}</sff-mode>
                {% for interface in sfinterfaces %}
                    <interface>
                        <name>sf-{{ interface }}</name>
                        <logical-port>{{ interface }}</logical-port>
                        <classifier-list>VLAN{{ vlanid }}</classifier-list>
                    </interface>
                {% endfor %}
            {% endif %}
            </sff>
        </sffs>
    </config>
    ''')

editSfs = Template('''
    <config>
        <sfs xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-sf">
            <sf operation="{{ operation }}">
            <sf-name>{{ vnfname }}</sf-name>
            {% if operation == "replace"%}
            <sfo>
                <image-mgmt>
                <image-ref>{{ vnfname }}</image-ref>
                </image-mgmt>
                <sfo-metadata>
                    <cpus>{{ numcpus }}</cpus>
                    <memory>{{ mem }}</memory>
                </sfo-metadata>
                <network-interface>
                    <name>mgmt</name>
                    <network-type>default</network-type>
                </network-interface>
                {% for sfIf in sfinterfaces %}
                <network-interface>
                    <name>SFvnet{{ sfIf }}</name>
                    <network-type>vhost</network-type>
                    <logical-port>vnet-{{ sfIf }}</logical-port>
                </network-interface>
                {% endfor %}
            </sfo>
            {% endif %}
            </sf>
        </sfs>
    </config>
    ''')

startSfs = Template('''
    <config>
        <sfs xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-sf">
            <sf>
            <sf-name>{{ vnfname }}</sf-name>
            <sf-operation>
                <state>start</state>
            </sf-operation>
            </sf>
        </sfs>
    </config>
''')


downloadFile = Template('''
        <config>
            <files xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-file-mgmt">
                <file>
                    <file-name>{{ image }}</file-name>
                    <file-mgmt>
                        <file-identifier>{{ image }}</file-identifier>
                        <file-download-uri>{{ image_path }}{{ image }}.qcow2</file-download-uri>
                        <file-download-size>{{ image_size }}</file-download-size>
                        <file-max-size>{{ image_max_size }}</file-max-size>
                        <checksum-uri>{{ image_path }}{{ image }}.md5</checksum-uri>
                        <checksum-type>md5</checksum-type>
                        <username>{{ sftp_user }}</username>
                        <password>{{ sftp_pwd }}</password>
                    </file-mgmt>
                </file>
            </files>
        </config>
''')

downloadStart = Template('''
            <file-action xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-file-mgmt">
                    <file-name>{{ image }}</file-name>
                    <action>download</action>
            </file-action>
''')


editFds = Template('''
    <config>
        <fds xmlns="urn:ciena:params:xml:ns:yang:ciena-pn:ciena-mef-fd">
            <fd>
                <name>v{{ vlanid }}</name>
                <mode>vpls</mode>
            </fd>
        </fds>
    </config>
''')


editInterfaces = Template('''
    <config>
        <interfaces xmlns="http://openconfig.net/yang/interfaces">
            <interface>
                <name>int{{ port }}v{{ vlanid }}</name>
                <config>
                    <name>int{{ port }}v{{ vlanid }}</name>
                    <mtu>1500</mtu>
                    <type xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces">ip</type>
                    <admin-status xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces">true</admin-status>
                    <role xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces" xmlns:cn-if="http://ciena.com/ns/yang/ciena-openconfig-interfaces">cn-if:data</role>
                    <vrfName xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces">default</vrfName>
                    <stats-collection xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces">on</stats-collection>
                    <underlay-binding xmlns="http://ciena.com/ns/yang/ciena-underlay-binding">
                        <config>
                            <fd>v{{ vlanid }}</fd>
                        </config>
                    </underlay-binding>
                </config>
                <ipv4 xmlns="http://ciena.com/ns/yang/ciena-openconfig-if-ip">
                    <addresses>
                        <address>
                            <ip>{{ portIp }}</ip>
                            <config>
                                <ip>{{ portIp }}</ip>
                                <prefix-length>30</prefix-length>
                            </config>
                        </address>
                    </addresses>
                </ipv4>
            </interface>
        </interfaces>
    </config>

''')

editIsisInterface = Template('''
    <config>
        <isis xmlns="http://ciena.com/ns/yang/ciena-isis">
            <instance>
                <tag>ISIS1</tag>
                <interfaces>
                    <interface>
                        <name>int{{ port }}v{{ vlanid }}</name>
                        <interface-type>point-to-point</interface-type>
                        <level-type>level-{{ isislvl }}</level-type>
                        <lsp-interval>33</lsp-interval>
                        <lsp-retransmit-interval>5</lsp-retransmit-interval>
                        <hello-padding>true</hello-padding>
                        <ipv4-unicast-default-disable>false</ipv4-unicast-default-disable>
                        <level-1>
                        <hello-interval>10</hello-interval>
                        <hello-multiplier>3</hello-multiplier>
                        <csnp-interval>10</csnp-interval>
                        <priority>64</priority>
                        <metric>10</metric>
                        <wide-metric>10</wide-metric>
                        <lfa-candidate-enable>true</lfa-candidate-enable>
                        </level-1>
                        <level-2>
                        <hello-interval>10</hello-interval>
                        <hello-multiplier>3</hello-multiplier>
                        <csnp-interval>10</csnp-interval>
                        <priority>64</priority>
                        <metric>10</metric>
                        <wide-metric>10</wide-metric>
                        <lfa-candidate-enable>true</lfa-candidate-enable>
                        </level-2>
                        <bfd>
                            <enable>false</enable>
                        </bfd>
                    </interface>
                </interfaces>
            </instance>
        </isis>
    </config>
''')

editFps = Template('''
    <config>
        <fps xmlns="urn:ciena:params:xml:ns:yang:ciena-pn:ciena-mef-fp">
            <fp>
                <name>p{{ port }}v{{ vlanid }}</name>
                <fd-name>v{{ vlanid }}</fd-name>
                <logical-port>{{ port }}</logical-port>
                <mtu-size>9000</mtu-size>
                <classifier-list-precedence>{{ vlanid}}</classifier-list-precedence>
                <classifier-list>VLAN{{ vlanid }}</classifier-list>
                <stats-collection>on</stats-collection>
                <egress-l2-transform>
                    <egress-name>push-0x8100.{{ vlanid }}.7</egress-name>
                    <vlan-stack>
                        <tag>1</tag>
                        <push-tpid>tpid-8100</push-tpid>
                        <push-pcp>pcp-7</push-pcp>
                        <push-vid>{{ vlanid }}</push-vid>
                    </vlan-stack>
                </egress-l2-transform>
            </fp>
        </fps>
    </config>
''')

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

sr_filter = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
          <segment-routing xmlns="urn:ciena:params:xml:ns:yang:ciena-pn:ciena-sr">
          </segment-routing>
        </filter>
    '''




nodes = {"3906_1": "10.181.35.55",
        "3906_2": "10.181.35.57",
        "5170_93": "10.181.34.2",
        "5170_94": "10.181.34.218",
        "5162_46": "10.181.34.72",
        }


creds = {'ip': "10.181.35.57",
        'user': 'user',
        'pwd': 'ciena123'
        }

imageSpecs = {
    'sftp_user': 'serge',
    'sftp_pwd': 'ciena123',
    "image_path": 'sftp://10.181.35.52/home/serge/images/',
    "vyos": {
        "image_size": 365,
        "image_max_size": 2000
    }
}


@click.group()
def cli():
    pass


###### Show commands ########
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

@show.command()
def sr():
    dnfvi_obj = get_nc_obj(creds, sr_filter)
    print(dnfvi_obj)
    view_sr(dnfvi_obj)


###### Create commands ########
@cli.group()
def create():
    pass

@create.command()
@click.argument('vlanid')
def classifier(vlanid):
    vlanIdDict = {'operation': 'replace', 'vlanid': vlanid}
    rendered_template = editClassifiers.render(vlanIdDict)
    print(rendered_template)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)

@create.command()
@click.argument('mode', nargs=1)
@click.argument('vlanid', nargs=1)
@click.argument('sfinterfaces', nargs=-1)
def sffs(mode, vlanid, sfinterfaces):
    varsDict = {'operation': 'replace', 'mode': mode, 'sfinterfaces': sfinterfaces, 'vlanid': vlanid}
    rendered_template = editSffs.render(varsDict)
    print(rendered_template)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)


@create.command()
@click.argument('vnfname', nargs=1)
@click.argument('numcpus', nargs=1)
@click.argument('mem', nargs=1)
@click.argument('sfinterfaces', nargs=-1)
def sfs(vnfname, numcpus, mem, sfinterfaces):
    varsDict = {'operation': 'replace', 'vnfname': vnfname, 'numcpus': numcpus, 'mem': mem, 'sfinterfaces': sfinterfaces}
    rendered_template = editSfs.render(varsDict)
    print(rendered_template)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)

@create.command()
@click.option('--isislvl', default=1, help="Specify ISIS level '1' or '2'. Default =1")
@click.argument('ip_and_mask', nargs=1)
@click.argument('port', nargs=1)
@click.argument('vlanid', nargs=1)
def ipinterface(ip_and_mask, port, vlanid, isislvl):
    """ Creates a port IP Interface and associated objects incl optionals.
        Format is: 'tenx create ipinterface 10.181.37.1/30 20 668'. """
    vlanIdDict = {'operation': 'replace', 'vlanid': vlanid}
    rendered_template = editClassifiers.render(vlanIdDict)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)
    rendered_template = editFds.render(vlanIdDict)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)
    maskIndex = ip_and_mask.find("/")
    portIp = ip_and_mask[0:maskIndex]
    mask = ip_and_mask[maskIndex+1:]
    vlanIdDict = {'operation': 'replace', 'vlanid': vlanid, 'portIp': portIp, 'port': port}
    rendered_template = editInterfaces.render(vlanIdDict)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)
    objDict = {'operation': 'replace', 'vlanid': vlanid, 'port': port, 'isislvl': isislvl}
    rendered_template = editIsisInterface.render(objDict)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)
    objDict = {'operation': 'replace', 'vlanid': vlanid, 'port': port}
    rendered_template = editFps.render(objDict)
    print(rendered_template)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)



###### Delete commands ########
@cli.group()
def delete():
    pass

@delete.command()
@click.argument('vlanid')
def classifier(vlanid):
    vlanIdDict = {'operation': 'delete','vlanid': vlanid}
    rendered_template = editClassifiers.render(vlanIdDict)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)

@delete.command()
@click.argument('vlanid')
def sffs(vlanid):
    vlanIdDict = {'operation': 'delete','vlanid': vlanid}
    rendered_template = editSffs.render(vlanIdDict)
    print(rendered_template)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)

@delete.command()
@click.argument('vnfname')
def sfs(vnfname):
    varsDict = {'operation': 'delete','vnfname': vnfname}
    rendered_template = editSfs.render(varsDict)
    print(rendered_template)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)


###### Start SFS command ########
@cli.group()
def start():
    pass

@start.command()
@click.argument('vnfname')
def sfs(vnfname):
    varsDict = {'operation': 'delete','vnfname': vnfname}
    rendered_template = startSfs.render(varsDict)
    print(rendered_template)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)


###### Download DNFVI File/image command ########
@cli.group()
def download():
    pass

@download.command()
@click.argument('image')
def file(image):
    varsDict = {'image': image,
                'sftp_user': imageSpecs['sftp_user'],
                'sftp_pwd': imageSpecs['sftp_pwd'],
                'image_path': imageSpecs['image_path'],
                'image_size': imageSpecs[image]['image_size'],
                "image_max_size": imageSpecs[image]['image_max_size'] }
    rendered_template = downloadFile.render(varsDict)
    print(rendered_template)
    dnfvi_obj = edit_nc_obj(creds, rendered_template)

@download.command()
@click.argument('image')
def start(image):
    varsDict = {'image': image}
    rendered_template = downloadStart.render(varsDict)
    print(rendered_template)
    dnfvi_obj = send_rpc(creds, rendered_template)


####### Set Node Commands #########
@cli.group()
def set():
    pass

@set.command()
@click.argument('name')
def node(name):
    if name in nodes:
        file = open("/home/slaviole/activenode.txt", "w")
        file.write(name)
        file.close()
        print("Addressed node is set to " + name)
    else:
        print("Nodename is not in list of valid nodes. Please try again.")

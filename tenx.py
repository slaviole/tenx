#!/home/slaviole/Projects/cliTools/venv/bin/python

from ncclient import manager
import untangle
import click
#import yaml


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


classifiers_filter = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ncx="http://netconfcentral.org/ns/yuma-ncx">
          <classifiers xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-mef-classifier">
            <classifier>
            </classifier>
          </classifiers>
        </filter>
        '''

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

        data = netconf_manager.get(classifiers_filter)
    data_str = str(data)
    d_obj = untangle.parse(data_str)
    return d_obj





creds = {'ip': '10.181.35.55', 'user': 'user', 'pwd': 'ciena123'}

@click.group()
def cli():
    pass

@cli.command()
def show():
    dnfvi_obj = get_nc_obj(creds)
    view_clsfr(dnfvi_obj)

if __name__ == "__main__":
    cli()

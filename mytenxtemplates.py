from jinja2 import Template

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
                    <logical-port>{{ sfIf }}</logical-port>
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
        {% for fd in fds %}
            <fd operation="{{ operation }}">
                <name>FD{{ fd.vlanid }}</name>
                {% if operation == "replace" %}
                <mode>vpls</mode>
                {% endif %}
            </fd>
        {% endfor %}
        </fds>
    </config>
''')

editFps = Template('''
    <config>
        <fps xmlns="urn:ciena:params:xml:ns:yang:ciena-pn:ciena-mef-fp">
            {% for fp in fps %}
            <fp operation="{{ operation }}">
                <name>{{ fp }}</name>
                {% if operation == "replace" %}
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
                {% endif %}
            </fp>
            {% endfor %}
        </fps>
    </config>
''')

createTargetLdp = Template('''
    <config>
    <ldp xmlns="http://ciena.com/ns/yang/ciena/ciena-ldp">
        <instance>
        <tag>default</tag>
        <target-ldp>
            <peers>
            <address>{{ peerip }}</address>
            <hello-interval>5</hello-interval>
            <hello-holdtime>15</hello-holdtime>
            </peers>
        </target-ldp>
        </instance>
    </ldp>
    </config>
''')



editInterfaces = Template('''
    <config>
        <interfaces xmlns="http://openconfig.net/yang/interfaces">
           {% for interface in interfaces %}
            {% if operation == "remove" %}
                <interface xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="{{ operation }}">
                    <name>{{  interface.name }}</name>
                </interface>
            {% endif %}
            {% if operation == "replace" %}
            <interface xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="{{ operation }}">
                <name>{{ interface.name }}</name>
                <config>
                    <name>{{ interface.name }}</name>
                    <mtu>1500</mtu>
                    <type xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces">ip</type>
                    <admin-status xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces">true</admin-status>
                    <role xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces" xmlns:cn-if="http://ciena.com/ns/yang/ciena-openconfig-interfaces">cn-if:data</role>
                    <vrfName xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces">default</vrfName>
                    <stats-collection xmlns="http://ciena.com/ns/yang/ciena-openconfig-interfaces">on</stats-collection>
                    <underlay-binding xmlns="http://ciena.com/ns/yang/ciena-underlay-binding">
                        <config>
                            <fd>FD{{ interface.vlanid }}</fd>
                        </config>
                    </underlay-binding>
                </config>
                <ipv4 xmlns="http://ciena.com/ns/yang/ciena-openconfig-if-ip">
                    <addresses>
                        <address>
                            <ip>{{ interface.portIp }}</ip>
                            <config>
                                <ip>{{ interface.portIp }}</ip>
                                <prefix-length>{{ interface.mask }}</prefix-length>
                            </config>
                        </address>
                    </addresses>
                </ipv4>
            </interface>
            {% endif %}
            {% endfor %}
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


editDhcp = Template('''
    <config>
        <dhcp-client xmlns="http://www.ciena.com/ns/yang/ciena-dhcp">
            {% for interface in interfaces %}
            <client xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="remove" xmlns="http://www.ciena.com/ns/yang/ciena-dhcp-multi">
                <interface-name>{{ interface }}</interface-name>
            </client>
            {% endfor %}
        </dhcp-client>
    </config>
''')


editDhcpv6 = Template('''
    <config>
        {% for interface in interfaces %}
        <dhcpv6-client xmlns="http://www.ciena.com/ns/yang/ciena-dhcpv6-client">
            <client xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="remove">
                <interface-name>{{ interface }}</interface-name>
            </client>
        </dhcpv6-client>
        {% endfor %}
    </config>
''')

# NSX for vSphere Ansible Modules

This repository contains a number of Ansible modules, written in Python, that can be used
to create, read, update and delete objects in NSX for vSphere.

# Version notice

Due to the latest changes to the way schemas are handled in the nsxraml file starting with NSX-v version 6.2.3, nsxansible requires nsxramlclient 2.0.0 or later. To upgrade the nsxramlclient you can do a ``sudo pip install --upgrade nsxramlclient``. Also please use the latest version of the RAML spec.

## Requirements

This module requires the NSX for vSphere RAML spec (RAML based documentation).
The latest version of the NSX for vSphere RAML spec (raml file + schema files) can be found and downloaded here: http://github.com/vmware/nsxraml.

The Python based ``nsxramlclient`` must also be installed and needs to be on version 2.0.0. Example of installing using pip:
```sh
sudo pip install nsxramlclient
```
More details on this Python client for the NSX for vSphere API can be found here: http://github.com/vmware/nsxramlclient. Additional details on installation is also available.

In addition, the 'vcenter_gather_facts' and 'deploy_nsx_ova' modules require that you have the vCenter python client 'Pyvmomi' installed. Example of installing PyVmomi using pip:
```sh
sudo pip install pyvmomi
```
More details on this Python client for vCenter can be found here: http://github.com/vmware/pyvmomi. Additional details on installation is also available.

The 'deploy_nsx_ova' module also requires that the machine on which the play is executed has ``ovftool`` installed. 
Ovftool is part of VMware Fusion on Mac, and can be installed on most Linux systems. For more information see https://www.vmware.com/support/developer/ovf/ 

## How to use these modules

Before using these modules the library from ``nsxansible`` needs to be either copied into the top level ansible directory where playbooks are stored or there needs to be a soft link to the library directory.

All modules need to be executed on a host that has ``nsxramclient`` installed and the host must have access to a copy of the NSX RAML File. In most deployments this likely to be localhost.
```yaml
---
- hosts: localhost
  connection: local
  gather_facts: False
```
Each module needs an array called ```nsxmanager_spec``` with following parameters supplied:
- The location of the NSX-v RAML file describing the NSX for vSphere API
- The NSX Manager where the API is running. Can be referenced by either a hostname or an IP Address.
- The NSX Manager username
- The NSX Manager password for the above user

These parameters are usually placed in a common variables file:

`answerfile.yml`
```yaml
nsxmanager_spec: 
  raml_file: '/raml/nsxraml/nsxvapiv614.raml'
  host: 'nsxmanager.invalid.org'
  user: 'admin'
  password: 'vmware'
```
`test_logicalswitch.yml`
```yaml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile.yml
  tasks:
  - name: logicalSwitch Operation
    nsx_logical_switch:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      transportzone: "TZ"
      name: "TestLS"
      controlplanemode: "UNICAST_MODE"
      description: "My Great Logical Switch"
    register: create_logical_switch

  - debug: var=create_logical_switch
```
The example shows thes ```nsxmanager_spec``` is read out of the file ```answerfile.yml```.

## Module specific parameters

Every module has specific parameters that are explained in the following sections:

###  Module `nsx_logical_switch`
##### Create, update and delete logical Switches
- state: 
present or absent, defaults to present
- name: 
Mandatory: Name of the logical switch. Updating the name creates a new switch as it is the unique
identifier.
- transportzone: 
Mandatory: Name of the transport zone in which the logical switch is created.
- controlplanemode:
Mandatory: Control plane mode for the logical switch. The value can be 'UNICAST_MODE',
'HYBRID_MODE' or 'MULTICAST_MODE'. Default is 'UNICAST_MODE'.
- description:
Optional: Free text description for the logical switch.

Example:
```yaml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile.yml
  tasks:
  - name: logicalSwitch Operation
    nsx_logical_switch:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: absent
      transportzone: "TZ"
      name: "TestLS"
      controlplanemode: "UNICAST_MODE"
      description: "My Great Logical Switch"
    register: create_logical_switch

  #- debug: var=create_logical_switch
```

###  Module `nsx_vc_registration`
##### Registers NSX Manager to VC or changes the registration

- vcenter: 
Mandatory: Hostname or IP address of the vCenter server to which NSX Manager should be registered/
- vcusername:
Mandatory: Username on the vCenter that should be used to register NSX Manager.
- vcpassword:
Mandatory: Password of the vCenter user used to register NSX Manager.
- vccertthumbprint: 
Mandatory if 'accept_all_certs' is not 'True': Certificate thumbprint of vCenter service.
- accept_all_certs:
Mandatory if 'vccertthumbprint' is not supplied: If set to 'True', NSX Manager will be connected to any vCenter Server
without checking the certificate thumbprint

*Note: 'accept_all_certs' and 'vccertthumbprint' are mutualy exclusive*

Example:
```yaml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: NSX Manager VC Registration
    nsx_vc_registration:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      vcenter: 'testvc.emea.nicira'
      vcusername: 'administrator@vsphere.local'
      vcpassword: 'vmware'
      #vccertthumbprint: '04:9D:9B:64:97:73:89:AF:16:4F:60:A0:F8:59:3A:D3:B8:C4:4B:A2'
      accept_all_certs: true
    register: register_to_vc

#  - debug: var=register_to_vc
```

### Module `nsx_sso_registration`
##### Registers NSX Manager to SSO or changes and deletes the SSO Registration

- state:
present or absent, defaults to present
- sso_lookupservice_url:
Mandatory: SSO Lookup Service url. Example format: 'lookupservice/sdk'
- sso_lookupservice_port:
Mandatory: SSO Lookup Service port. E.g. '7444'
- sso_lookupservice_server: 
Mandatory: SSO Server Hostname, FQDN or IP Address. E.g. 'testvc.emea.nicira'
- sso_admin_username: 
Mandatory: Username to register to SSO. Typically thi sis administrator@vsphere.local
- sso_admin_password:
Mandatory: Password of the SSO user used to register.
- sso_certthumbprint: 
Mandatory if 'accept_all_certs' is not 'True': Certificate thumbprint of SSO service.
- accept_all_certs:
Mandatory if 'sso_certthumbprint' is not supplied: If set to 'True', NSX Manager will be connected to any SSO Server without checking the certificate thumbprint

*Note: 'accept_all_certs' and 'vccertthumbprint' are mutualy exclusive*

Example:
```yaml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: NSX Manager SSO Registration
    nsx_sso_registration:
      state: present
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      sso_lookupservice_url: 'lookupservice/sdk'
      sso_lookupservice_port: 7444
      sso_lookupservice_server: 'testvc.emea.nicira'
      sso_admin_username: 'administrator@vsphere.local'
      sso_admin_password: 'vmware'
      #sso_certthumbprint: 'DE:D7:57:DC:D3:E4:40:4E:AA:4A:3A:56:91:B0:48:92:6E:68:E6:03'
      accept_all_certs: true
    register: register_to_sso

#  - debug: var=register_to_sso
```

### Module `nsx_ippool`
##### Create, update and delete an IP Pool in NSX Manager

- state:
present or absent, defaults to present
- name: 
Mandatory: Name of the IP Pool. Updating the name creates a new IP Pool as it is the unique
identifier.
- start_ip:
Mandatory: Start IP address in the pool.
- end_ip:
Mandatory: End IP address in the pool.
- prefix_length:
Mandatory: Prefix length of the IP pool (i.e. the number of bits in the subnet mask).
- gateway:
Optional: Default gateway in the IP pool.
- dns_server_1:
Optional: First DNS server in the pool.
- dns_server_2:
Optional: Second DNS server in the pool.

Returns:
ippool_id variable will contain the IP Pool Id in NSX (e.g. "ipaddresspool-2") if the ippool is created, updates or un-changed.
None will be returned when the IP Pool state is absent.

Example:
```yaml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile.yml
  tasks:
  - name: Controller IP Pool creation
    nsx_ippool:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      name: 'ansible_controller_ip_pool'
      start_ip: '172.17.100.65'
      end_ip: '172.17.100.67'
      prefix_length: '24'
      gateway: '172.17.100.1'
      dns_server_1: '172.17.100.11'
      dns_server_2: '172.17.100.12'
    register: create_ip_pool

  #- debug: var=create_ip_pool
```

Example return:
```yaml
- debug: var=controller_ip_pool.ippool_id
```
```sh
ok: [localhost] => {
    "var": {
        "controller_ip_pool.ippool_id": "ipaddresspool-10"
    }
}
```

### Module `nsx_controllers`
##### Deploy individual controllers, full 3 node clusters as well as 1 node lab deployments including syslog configuration

- state:
present or absent, defaults to present
- deploytype: 
lab, single of full, defaults to full
 - lab: Only a single controller gets deployed. If there are already controllers deployed in the setup, 'lab' will leave the environment unchanged, and will only apply changes to syslog if needed
 - single: This will create a new controller if the number of existing controllers in the setup is 0, 1 or 2. If the number of existing controllers is 3, 'single'  will leave the environment unchanged, and only apply changes to syslog if needed. You can use this option if you want to deploy a controller cluster with individual nodes placed into e.g. different datastores, clusters or networks
 - full: This will create a full cluster of 3 controller nodes. If there is any existing controller found, 'full' will leave the environment unchanged and only apply changes to syslog if needed. Use this option if you want to deploy a full 3 node cluster, and all node should be placed on the the same datastore, cluster, network, etc.
- syslog_server: 
Optional: This will set the syslog server on **all** controller nodes found in the setup.
  - If not set or left out in the play: If no value is set, but existing controllers have syslog configured, all controller syslog configuration will be blanked out
  - SyslogIP: If the IP of the syslog server is passed, if will be configured on **all** controller nodes found in the setup
- ippool_id:
Mandatory: The IP Pool used to assign IP Addresses to controller nodes
- resourcepool_moid:
Mandatory: The vSphere Managed Object Id of the vSphere cluster or resource pool to deploy the controller into
- host_moid:
Optional: The vSphere Managed Object Id of an individual host where to place the controller in
- datastore_moid:
Mandatory: The vSphere Managed Object Id of a datastore to deploy the controller into
- network_moid:
Mandatory: The vSphere Managed Object Id of the management network the controller should be using
- password:
Mandatory: The controller CLI and SSH password of the 'admin' user


Example:
```yaml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: Controller Cluster Creation
    nsx_controllers:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      deploytype: 'lab'
      syslog_server: '172.17.100.129'
      ippool_id: 'ipaddresspool-2'
      resourcepool_moid: 'domain-c26'
      #host_moid: 'host-29'
      datastore_moid: 'datastore-37'
      network_moid: 'dvportgroup-36'
      password: 'VMware1!VMware1!'
    register: create_controller_cluster

  #- debug: var=create_controller_cluster
```

### Module `nsx_segment_id_pool`
##### Configure or delete the VXLAN Segment Id Pool (VXLAN Id space) and optionally associated Multicast Range

- state:
present or absent, defaults to present
- idpoolstart:
Id Pool start Id. Defaults to 5000 if not supplied
- idpoolend:
Id Pool end Id. Defaults to 15000 if not supplied
- mcast_enabled:
If set to true, a multicast range will be configured alongside the Segment Id. Defaults to false if not set. 
Setting mcast_enabled to false for an existing segment pool will remove the multicast pool but keep the segment pool
- mcastpoolstart:
Starting Multicast IP Address. Defaults to '239.0.0.0' if not set explicitly. Only used if 'mcast_enabled' is 'true'
- mcastpoolend:
Ending Multicast IP Address. Defaults to '239.255.255.255' if not set explicitly. Only used if 'mcast_enabled' is 'true'

Example:
```yaml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: Segment Pool Configuration
    nsx_segment_id_pool:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      #idpoolstart: 5000
      #idpoolend: 15000
      mcast_enabled: true
      #mcastpoolstart: '239.0.0.0'
      #mcastpoolend: '239.255.255.255' 
    register: create_segment_pool

  #- debug: var=create_segment_pool
```

### Module `nsx_cluster_prep`
##### Prepares the vSphere Clusters for the use with NSX (Installs the VIBs)

- state:
present or absent, defaults to present. 
Present will start the cluster prep (install VIBs) if the cluster is in the 'UNKNOWN' state. 
If the cluster is in 'RED' or 'YELLOW' state, the module will fail and ask for manual intervention.
Absent will un-prep the cluster (uninstall the VIBs). This will leave the cluster in the 'RED'
state, requiring the vSphere Admin to reboot the hypervisors to complete the VIB uninstall
- cluster_moid:
Mandatory: The vSphere managed object Id of the cluster to prep or un-prep

Example:
```yml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: Cluster preparation
    nsx_cluster_prep:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      cluster_moid: 'domain-c26'
    register: cluster_prep

  #- debug: var=cluster_prep
```

### Module `nsx_vxlan_prep`
##### Prepares the vSphere Cluster and VDS for VXLAN (Configures VTEP Interfaces)

- state:
present or absent, defaults to present. 
Present will configure VXLAN according to the passed details or defaults, 
Absent will un-configure VXLAN (remove the VTEPs).
- cluster_moid:
Mandatory: The vSphere managed object Id of the cluster to configure VXLAN VTEPs on
- dvs_moid:
Mandatory: The vSphere managed object Id of the distributed vSwitch (dvs) used as the transport
network dvs
- ippool_id:
Optional: If not passed the VTEPs will be set to receive its IP Address via DHCP. If set to
an valid nsx ippool id, the VTEP IP will be allocated from the IP Pool
- vlan_id:
Optional: Defaults to 0 (untagged), if set to a value this specifies the VLAN Id for the VTEP
- vmknic_count:
Optional: Defaults to 1, number of VTEP Interfaces to deploy. This is only working for the teaming modes 'LOADBALANCE_SRCID' and 'LOADBALANCE_SRCMAC' and when multiple uplinks are present
- teaming:
Optional: Defaults to 'FAILOVER_ORDER'. This specifies the uplink teaming mode for the VTEP port-group. Valid values are: FAILOVER_ORDER,ETHER_CHANNEL,LACP_ACTIVE,LACP_PASSIVE,LOADBALANCE_SRCID,LOADBALANCE_SRCMAC & LACP_V2
- mtu:
Optional: Defaults to 1600, the MTU configured for the VTEP and VTEP port-group

Example:
```yml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: Cluster VXLAN Preparation
    nsx_vxlan_prep:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      cluster_moid: 'domain-c26'
      dvs_moid: 'dvs-34'
      ippool_id: 'ipaddresspool-3'
      #vlan_id: 100
      #vmknic_count: 1
      #teaming: 'ETHER_CHANNEL'
      #mtu: 9000
    register: vxlan_prep

  #- debug: var=vxlan_prep
```

### Module `vcenter_gather_moids`
##### Retrieves Managed Object Ids (moids) from vCenter to use them in the NSX plays

The NSX modules often need vCenter moids to be presented to them. To retrieve them dynamically from vCenter in
a playbook, you can use the `vcenter_gather_moids` module.

- hostname:
Mandatory: The Hostname, FQDN or IP Address of your vCenter Server
- username:
Mandatory: The Username used to access you vCenter
- password:
Mandatory: The password of your vCenter users
- datacenter_name:
Mandatory: The name of the datacenter object to search, and to search subsequent objects in
- cluster_names:
Optional: The name of the searched cluster object 
- resourcepool_names:
Optional: The name of the searched resourcepool object 
- dvs_names:
Optional: The name of the searched dvs object 
- portgroup_names:
Optional: The name of the searched portgroup object 
- datastore_names:
Optional: The name of the searched datastore object 

NOTE: All Optional Parameters are single strings. One of the optional parameters needs to be present. Only one parameters
can be searched in a single task:


Example:
```yml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: Gather vCenter MOIDs
    vcenter_gather_moids:
      hostname: 'testvc.emea.nicira'
      username: 'administrator@vsphere.local'
      password: 'vmware'
      datacenter_name: 'nsxlabdc'
      cluster_name: 'compute'
      #resourcepool_name: 'test_rp'
      #dvs_name: 'TransportVDS'
      #portgroup_name: 'VM Network'
      #datastore_name: 'NFS-Storage03'
    register: gather_moids_output

  - debug: msg="The searched moid is {{ gather_moids_output.object_id }}"
```

The output of the above example is:

```sh
ok: [localhost] => {
    "msg": "The searched moid is domain-c28"
}
```

The moid of the searched object can be accessed using the 'object_id' attribute of the registered variable. 
E.g. in the above example you can reference to the cluster with ```{{ gather_moids_output.object_id }}```

### Module `nsx_deploy_ova`
##### Deploys the OVA of NSX Manager into a vSphere Cluster

This module uses 'ovftool' to deploy the NSX Manager OVA into a vSphere Cluster. It also uses PyVmomi to check the
cluster for VMs with the same name to make this module idempotent. In addition it checks if the NSX Manager API is reachable
and response both on a fresh deployment, as well as if NSX Manager already exists

- ovftool_path:
Mandatory: The filesystem path to the ovftool. This should be '/usr/bin' on most Linux systems, and '/Applications' on Mac
- vcenter:
Mandatory: The vCenter Server in which the OVA File will be deployed
- vcenter_user:
Mandatory: The vCenter user to use
- vcenter_passwd:
Mandatory: The vCenter user password
- datacenter:
Mandatory: The vCenter datacenter object to deploy NSX Manager into
- datastore:
Mandatory: The datastore used to place the NSX Manager root disk
- portgroup:
Mandatory: The portgroup of the management network to patch NSX Manager into
- cluster:
Mandatory: The cluster in which NSX Manager will be deployed
- vmname:
Mandatory: The VM name of NSX Manager in the vCenter Inventory
- hostname:
Mandatory: The Hostname NSX Manager will be configured to use
- dns_server:
Mandatory: The DNS Server NSX Manager will be configured to use
- dns_domain:
Mandatory: The DNS Domain NSX Manager will be configured to use
- gateway:
Mandatory: The default gateway on the management network
- netmask:
Mandatory: The netmask of the management network
- ip_address:
Mandatory: The netmask of the management network
- admin_password:
Mandatory: The password of the 'admin' user in NSX Manager
- enable_password:
Mandatory: The 'enable' password for the NSX Manager CLI
- path_to_ova:
Mandatory: The filesystem path in which the NSX Manager OVA file can be found
- ova_file:
Mandatory: The NSX Manager OVA File to deploy

Example:
```yml
---
- hosts: jumphost
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: deploy nsx-man
    nsx_deploy_ova:
      ovftool_path: '/usr/bin'
      datacenter: 'YF-Sofia-Lab'
      datastore: 'storage03-NFS-10GE'
      portgroup: 'vlan100'
      cluster: 'management-and-edge'
      vmname: 'testnsx'
      hostname: 'testnsx.emea.nicira'
      dns_server: '172.17.100.11'
      dns_domain: 'emea.nicira'
      gateway: '172.17.100.1'
      ip_address: '172.17.100.61'
      netmask: '255.255.255.0'
      admin_password: 'vmware'
      enable_password: 'vmware'
      path_to_ova: '/home/nicira/ISOs'
      ova_file: 'VMware-NSX-Manager-6.1.4-2691049.ova'
      vcenter: '172.17.100.130'
      vcenter_user: 'administrator@vsphere.local'
      vcenter_passwd: 'vmware'
    register: deploy_nsx_man

#  - debug: var=deploy_nsx_man
```

### Module `nsx_transportzone`
##### Deploys, updates or deletes a new transport zone in NSX

- name:
Mandatory: name of the transport zone. Updating the name creates a new switch as it is the unique identifier
- state:
present or absent, defaults to present
- controlplanemode:
Mandatory: Default Control plane mode for logical switches in the transport zone. The value can be 'UNICAST_MODE',
'HYBRID_MODE' or 'MULTICAST_MODE'. Default is 'UNICAST_MODE'.
- cluster_moid_list:
Mandatory: A list of vSphere managed object ids of clusters that are part of the transport zone. The list can either be a single cluster like 'domain-c26', or a python list ['domain-c26', 'domain-c28'] or list items in the yaml format as documented in the example bellow. Changing the list will add or remove clusters from the TZ.

Example:
```yml
---
- hosts: localhost
  connection: local
  gather_facts: False
  vars_files:
     - answerfile_new_nsxman.yml
  tasks:
  - name: Transport Zone Creation
    nsx_transportzone:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: 'present'
      name: 'TZ1'
      controlplanemode: 'HYBRID_MODE'
      description: 'My Transport Zone'
      cluster_moid_list:
        - 'domain-c28'
        - 'domain-c26'
    register: transport_zone

#  - debug: var=transport_zone
```

### Module `nsx_edge_router`
##### Deploys, updates or deletes a NSX Edge Services Gateway in NSX

- name:
Mandatory: name of the Edge Services Gateway to be deployed
- state:
Optional: present or absent, defaults to present
- description:
Optional: A free text description for the ESG
- appliance size:
Optional: The ESG size, choices=['compact', 'large', 'xlarge', 'quadlarge'], defaults to 'large'
- resourcepool_moid:
Mandatory: The vCenter MOID of the ressource pool to deploy the ESG in
- datastore_moid:
Mandatory: The vCenter MOID of the datatore to deploy the ESG on
- datacenter_moid:
Mandatory: The vCenter MOID of the datacenter to deploy the ESG in
- interfaces:
Mandatory: A dictionary that holds the configuration of each vnic as a sub-dictionary. See the interfaces details section for more information
- default_gateway:
Optional: The IP Address of the default gateway
- routes:
Optional: A list of dictionaries holding static route configurations. See the route details section for more information
- username:
Optional: The username used for the CLI access to the ESG
- password:
Optional: The password used for the CLI access to the ESG
- remote_access:
Optional: true / false, is SSH access to the ESG enabled, defaults to false
- firewall:
Optional: true / false, is the ESG Firewall enabled, defaults to true
- ha_enabled:
Optional: true / false, deploy ESG as an HA pair, defaults to false
- ha_deadtime:
Optional: Sets the deadtime for Edge HA, defaults to 15

Example:
```yml
- name: ESG creation
    nsx_edge_router:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      name: 'ansibleESG_testplay'
      description: 'This ESG is created by nsxansible'
      resourcepool_moid: "{{ gather_moids_cl.object_id }}"
      datastore_moid: "{{ gather_moids_ds.object_id }}"
      datacenter_moid: "{{ gather_moids_cl.datacenter_moid }}"
      interfaces:
        vnic0: {ip: '10.114.209.94', prefix_len: 27, portgroup_id: "{{ gather_moids_upl_pg.object_id }}", name: 'Uplink vnic', iftype: 'uplink', fence_param: 'ethernet0.filter1.param1=1'}
        vnic1: {ip: '192.168.178.1', prefix_len: 24, logical_switch: 'transit_net', name: 'Internal vnic', iftype: 'internal', fence_param: 'ethernet0.filter1.param1=1'}
      default_gateway: '10.114.209.65'
      routes:
        - {network: '10.11.12.0/24', next_hop: '192.168.178.2', admin_distance: '1', mtu: '1500', description: 'very important route'}
        - {network: '10.11.13.0/24', next_hop: '192.168.178.2', mtu: '1600'}
        - {network: '10.11.14.0/24', next_hop: '192.168.178.2'}
      remote_access: 'true'
      username: 'admin'
      password: 'VMware1!VMware1!'
      firewall: 'false'
      ha_enabled: 'true'
    register: create_esg
    tags: esg_create
```

##### Interfaces Dict
Each vnic passed to the module in the interfaces dictionary variable is defined as a sub-dictionary with the following key / value pairs:

dict key: Each parent disctionary has the key set to the vnic id (e.g. vnic0), followed by a sub-directory with the vnic settings.

Sub-Directory:
- ip:
Mandatory: The IP Address of the vnic
- prefix_len:
Mandatory: The prefix length for the IP on the vnic, e.g. 24 for a /24 (255.255.255.0)
- if_type:
Mandatory: The interface type, either 'uplink' or 'internal'
- logical_switch:
Optional: The logical switch id to attach the ESG vnic to, e.g. virtualwire-10. NOTE: Either logical_switch or portgroupid need to be supplied.
- portgroupid:
Optional: The Portgroup MOID to attach the ESG vnic to, e.g. network-10. NOTE: Either logical_switch or portgroupid need to be supplied.
- fence_param:
Optional: Additional fence parameters supplied to the vnic, e.g. 'ethernet0.filter1.param1=1'

Example:
```yml
interfaces:
  vnic0: {ip: '10.114.209.94', prefix_len: 27, portgroup_id: "{{ gather_moids_upl_pg.object_id }}", name: 'Uplink vnic', iftype: 'uplink', fence_param: 'ethernet0.filter1.param1=1'}
  vnic1: {ip: '192.168.178.1', prefix_len: 24, logical_switch: 'transit_net', name: 'Internal vnic', iftype: 'internal', fence_param: 'ethernet0.filter1.param1=1'}
```

##### Routes list
Each route is passed to the module as a dictionary in a list. Each dictionary has the following key / value pairs:
- network:
Mandatory: The target network for the route, e.g. '10.11.12.0/24'
- next_hop:
Mandatory: The next hop IP for the route, e.g. '192.168.178.2'
- admin_distance:
Optional: The admin_distance to be used for this route
- mtu:
Optional: The MTU supported by this route
- description:
Optional: A free text description for the static route

Example:
```yml
routes:
  - {network: '10.11.12.0/24', next_hop: '192.168.178.2', admin_distance: '1', mtu: '1500', description: 'very important route'}
  - {network: '10.11.13.0/24', next_hop: '192.168.178.2', mtu: '1600'}
  - {network: '10.11.14.0/24', next_hop: '192.168.178.2'}
```


### Module `nsx_dlr`
##### Deploys, updates or deletes a Distributed Logical Router (DLR) in NSX

- name:
Mandatory: name of the DLR to be deployed
- state:
Optional: present or absent, defaults to present
- description:
Optional: A free text description for the DLR
- resourcepool_moid:
Mandatory: The vCenter MOID of the ressource pool to deploy the DLR control VM in
- datastore_moid:
Mandatory: The vCenter MOID of the datatore to deploy the DLR control VM on
- datacenter_moid:
Mandatory: The vCenter MOID of the datacenter to deploy the DLR control VM in
- mgmt_portgroup_moid:
Mandatory: The vCenter MOID of the portgroup used for the HA network and control VM management
- interfaces:
Mandatory: A list that holds the configuration of each interface as a dictionary. See the interfaces details section for more information
- default_gateway:
Optional: The IP Address of the default gateway
- routes:
Optional: A list of dictionaries holding static route configurations. See the route details section for more information
- username:
Optional: The username used for the CLI access to the DLR Control VM
- password:
Optional: The password used for the CLI access to the DLR Control VM
- remote_access:
Optional: true / false, is SSH access to the DLR Control VM enabled, defaults to false
- ha_enabled:
Optional: true / false, deploy DLR Control VM as an HA pair, defaults to false
- ha_deadtime:
Optional: Sets the deadtime for Edge HA, defaults to 15

Example:
```yml
  - name: DLR creation
    nsx_dlr:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      name: 'ansibleDLR'
      description: 'This DLR is created by nsxansible'
      resourcepool_moid: "{{ gather_moids_cl.object_id }}"
      datastore_moid: "{{ gather_moids_ds.object_id }}"
      datacenter_moid: "{{ gather_moids_cl.datacenter_moid }}"
      mgmt_portgroup_moid: "{{ gather_moids_pg.object_id }}"
      interfaces:
        - {name: 'Uplink vnic', ip: '192.168.178.2', prefix_len: 24, logical_switch: 'edge_ls', iftype: 'uplink'}
        - {name: 'Internal iface', ip: '172.16.1.1', prefix_len: 24, portgroup_id: "{{ gather_moids_pg.object_id }}", iftype: 'uplink'}
        - {name: 'Internal new', ip: '172.16.4.1', prefix_len: 26, logical_switch: 'new_lswitch_name', iftype: 'internal'}
      routes:
        - {network: '10.11.22.0/24', next_hop: '172.16.1.2', admin_distance: '1', mtu: '1500', description: 'very important route'}
        - {network: '10.11.23.0/24', next_hop: '172.16.1.2', mtu: '1600'}
        - {network: '10.11.24.0/24', next_hop: '172.16.4.2'}
        - {network: '10.11.25.0/24', next_hop: '172.16.4.2'}
      default_gateway: '192.168.178.1'
      remote_access: 'true'
      username: 'admin'
      password: 'VMware1!VMware1!'
      ha_enabled: 'true'
    register: create_dlr
    tags: dlr_create
```

##### Interfaces list
Each interface passed to the module in the interfaces list variable is defined as a dictionary with the following key / value pairs:

- ip:
Mandatory: The IP Address of the interface
- prefix_len:
Mandatory: The prefix length for the IP on the interface, e.g. 24 for a /24 (255.255.255.0)
- if_type:
Mandatory: The interface type, either 'uplink' or 'internal'
- logical_switch:
Optional: The logical switch id to attach the DLR Interface to, e.g. virtualwire-10. NOTE: Either logical_switch or portgroupid need to be supplied.
- portgroupid:
Optional: The Portgroup MOID to attach the DLR Interface to, e.g. network-10. NOTE: Either logical_switch or portgroupid need to be supplied.

Example:
```yml
interfaces:
  - {name: 'Uplink vnic', ip: '192.168.178.2', prefix_len: 24, logical_switch: 'edge_ls', iftype: 'uplink'}
  - {name: 'Internal iface', ip: '172.16.1.1', prefix_len: 24, portgroup_id: "{{ gather_moids_pg.object_id }}", iftype: 'uplink'}
  - {name: 'Internal new', ip: '172.16.4.1', prefix_len: 26, logical_switch: 'new_lswitch_name', iftype: 'internal'}
```

##### Routes list
Each route is passed to the module as a dictionary in a list. Each dictionary has the following key / value pairs:
- network:
Mandatory: The target network for the route, e.g. '10.11.12.0/24'
- next_hop:
Mandatory: The next hop IP for the route, e.g. '192.168.178.2'
- admin_distance:
Optional: The admin_distance to be used for this route
- mtu:
Optional: The MTU supported by this route
- description:
Optional: A free text description for the static route

Example:
```yml
routes:
  - {network: '10.11.12.0/24', next_hop: '192.168.178.2', admin_distance: '1', mtu: '1500', description: 'very important route'}
  - {network: '10.11.13.0/24', next_hop: '192.168.178.2', mtu: '1600'}
  - {network: '10.11.14.0/24', next_hop: '192.168.178.2'}
```

### Module `nsx_ospf`
##### enables, updates or deletes OSPF configurations in NSX for ESGs and DLRs

- state:
Optional: present or absent, defaults to present
- edge_name:
Mandatory: The name of the ESG or DLR to be configured for OSPF
- router_id:
Mandatory: The ESG or DLR Router id to be configured, e.g. configured as an IP Address
- graceful_restart:
Optional: true / false, is graceful restart enabled, defaults to true
- default_originate:
Optional: true / false, will the ESG or DLR announce its default route into OSPF, defaults to false
- protocol_address:
Unused for ESG, Mandatory for DLR: The IP address to be used to send OSPF message from
- forwarding_address:
Unused for ESG, Mandatory for DLR: The IP address to be used as the next-hop for the traffic
- logging:
Optional: true / false, will the ESG or DLR log state changes, defaults to false
- log_level:
Optional: Log level for OSPF state changes, choices=['debug', 'info', 'notice', 'warning', 'error', 'critical', 'alert', 'emergency'], defaults to 'info'
- areas:
Optional: A list of Dictionaries with Areas, See the Area details section for more information
- area_map:
Optional: A list of Dictionaries with Area to interface mappings, See the area_map details section for more information

Example:
```yml
  - name: Configure OSPF DLR
    nsx_ospf:
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      state: present
      edge_name: 'ansibleDLR'
      router_id: '172.24.1.3'
      default_originate: True
      graceful_restart: False
      logging: True
      log_level: debug
      forwarding_address: '172.24.1.2'
      protocol_address: '172.24.1.3'
      areas: 
        - { area_id: 10 }
      area_map:
        - { area_id: 10, vnic: "{{ dlr_uplink_index }}" }      
    register: ospf_dlr
    tags: ospf_dlr
```

##### Area list
Each Area is defined as a dictionary holding the following Key / Value pairs:

- area_id:
Mandatory: The Area id, e.g. 0
- type:
Optional: The area type, e.g. 'nssa' or 'normal', defaults to 'normal'
- authentication:
Optional: Authentication type, 'none', 'password' or 'md5', defaults to 'none'
- password:
Mandatory for Authentication types 'password' or 'md5', the password or md5 hash used to authenticate

NOTE: When Authentication types are used, the module will always report a change as the password can't be retrieved and check from NSX Manager

Example:
```yml
areas: 
  - { area_id: 0 }
  - { area_id: 61 }
  - { area_id: 59, type: 'nssa' }
  - { area_id: 62, type: 'nssa', authentication: 'password', password: 'mysecret' }
```

##### Area mapping list
Each Area / Interface mapping list is holding the following Key / Value pairs:

- area_id:
Mandatory: The Area Id, e.g. 0
- vnic:
Mandatory: The vnic Id to map the Area to, e.g. 0 for vnic0
- ignore_mtu:
Optional: true / false, Ignore MTU mismatches between OSPF interfaces, defaults to false
- hello:
Optional: The Hello Interval, defaults to 10
- dead:
Optional: The dead interval, defaults to 40
- cost:
Optional: The Interface Cost, default to 1
- priority:
Optional: The Interface Priority, defaults to 128

Example:
```yml
area_map:
  - { area_id: 0, vnic: 0, hello: 20}
  - { area_id: 61, vnic: 1, ignore_mtu: True , hello: 15, dead: 60, priority: 128, cost: 1}
```

### Module `nsx_redistribution`
##### enables, updates or deletes routing protocol redistribution in NSX for ESGs and DLRs (OSPF & BGP)

- ospf_state:
Mandatory: true / false, is redistribution enabled for OSPF
- bgp_state:
Mandatory: true / false, is redistribution enabled for BGP
- prefixes:
Optional: A list of dictionaries containing prefixes, See the prefixes details section for more information
- rules:
Optional: A list of dictionaries containing redistribution rules, See the rules details section for more information

Example:
```yml
  - name: Configure OSPF ESG
    nsx_redistribution:
      ospf_state: present
      bgp_state: present
      nsxmanager_spec: "{{ nsxmanager_spec }}"
      edge_name: 'ansibleESG'
      prefixes:
        - {name: 'testprfx1', network: '192.168.179.0/24'}
        - {name: 'testprfx2', network: '10.11.12.0/24'}
      rules:
        - {learner: 'ospf', priority: 0, static: false, connected: true, bgp: false, ospf: false, action: 'permit'}
        - {learner: 'ospf', priority: 1, static: 'true', connected: 'true', bgp: 'false', ospf: 'false', prefix: 'testprfx1', action: 'deny'}
        - {learner: 'bgp', priority: 1, connected: true, prefix: 'testprfx2', action: 'deny'}
        - {learner: 'bgp', priority: 0, connected: true, prefix: 'testprfx1'}
    register: redist
    tags: redist
```

##### Prefixes list
The prefixes variable holds a list of dictionaries with the following Key / Value pairs:

- name:
Mandatory: The name of the prefix list
- network:
Mandatory: The network to match, in the form of '<network>/<prefix_len>', e.g. '192.168.179.0/24'

Example:
```yml
prefixes:
  - {name: 'testprfx1', network: '192.168.179.0/24'}
  - {name: 'testprfx2', network: '10.11.12.0/24'}
```

##### Rules list
The rules variable holds a list of dictionaries with the following Key / Value pairs:

- learner:
Mandatory: The learner protocol, this can be 'bgp' or 'ospf'
- priority:
Mandatory: The priority (order) in which rules are applied, e.g. 0,1,2,3,...
- static:
Optional: true / false, reditribute static routes, defaults to false
- connected:
Optional: true / false, reditribute connected routes, defaults to false
- bgp:
Optional: true / false, reditribute bgp routes, defaults to false
- ospf:
Optional: true / false, reditribute ospf routes, defaults to false
- prefix:
Optional: A prefix list name to use as a filter for the routes
- action:
Optional: The action to apply with this rule, can be 'permit', 'deny', defaults to 'permit'

Example:
```yml
rules:
  - {learner: 'ospf', priority: 0, static: false, connected: true, bgp: false, ospf: false, action: 'permit'}
  - {learner: 'ospf', priority: 1, static: 'true', connected: 'true', bgp: 'false', ospf: 'false', prefix: 'testprfx1', action: 'deny'}
  - {learner: 'bgp', priority: 1, connected: true, prefix: 'testprfx2', action: 'deny'}
  - {learner: 'bgp', priority: 0, connected: true, prefix: 'testprfx1'}
```

## Example Playbooks and roles
### As part of this repo you will find example playbooks and roles:

#### Playbooks
`deployNsx.yml`
This is a playbook that can be used with the ``base-config-nsx`` and ``deploy-nsx-ova`` roles to deploy NSX 
in an existing vSphere cluster

#### Roles
`deploy-nsx-ova`: An example role that uses the ``nsx_deploy_ova`` module to deploy NSX Manager into a vSphere Cluster
`base-config-nsx`: An example role that creates all needed NSX Objects, Controllers, VIB and configuration for a base NSX deployment


## License

Copyright © 2015 VMware, Inc. All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.



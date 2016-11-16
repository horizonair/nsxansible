#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2015 VMware, Inc. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions
# of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


def get_ippool_id(session, searched_pool_name):
    try:
        ip_pools = session.read('ipPools',
                                uri_parameters={'scopeId':
                                                'globalroot-0'})['body']['ipamAddressPools']['ipamAddressPool']
    except TypeError:
        return None

    if type(ip_pools) is dict:
        if ip_pools['name'] == searched_pool_name:
            return ip_pools['objectId']
    elif type(ip_pools) is list:
        try:
            return [ip_pool['objectId'] for ip_pool in ip_pools if ip_pool['name'] == searched_pool_name][0]
        except IndexError:
            return None


def get_ippool_details(session, pool_object_id):
    return session.read('ipPool', uri_parameters={'poolId': pool_object_id})['body']

def main():
    module = AnsibleModule(
        argument_spec=dict(
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            ippool=dict(required=True),
        ),
        supports_check_mode=True
    )

    from nsxramlclient.client import NsxClient

    s = NsxClient(module.params['nsxmanager_spec']['raml_file'], module.params['nsxmanager_spec']['host'],
                  module.params['nsxmanager_spec']['user'], module.params['nsxmanager_spec']['password'])

    if module.params['ippool'] != None:
        ip_pool_objectid = get_ippool_id(s, module.params['ippool'])
        if not ip_pool_objectid:
            module.fail_json(changed=False, msg='pool not found')
        ippool_config = get_ippool_details(s, ip_pool_objectid)
        module.exit_json(changed=False, argument_spec=module.params, ippool_config=ippool_config,
                         ippool_id=ip_pool_objectid)
    else:
        module.fail_json(msg='specify a valid object type and search argument')
        
        
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: mso_schema
short_description: Manage schemas
description:
- Manage schemas on Cisco ACI Multi-Site.
author:
- Dag Wieers (@dagwieers)
options:
  schema:
    description:
    - The name of the schema.
    type: str
    aliases: [ name ]
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, query ]
    default: present
notes:
- Due to restrictions of the MSO REST API this module cannot create empty schemas (i.e. schemas without templates).
  Use the M(cisco.mso.mso_schema_template) to automatically create schemas with templates.
seealso:
- module: cisco.mso.mso_schema_site
- module: cisco.mso.mso_schema_template
extends_documentation_fragment: cisco.mso.modules
'''

EXAMPLES = r'''
- name: Remove schemas
  cisco.mso.mso_schema:v 
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    state: absent
  delegate_to: localhost

- name: Query a schema
  cisco.mso.mso_schema:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema 1
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all schemas
  cisco.mso.mso_schema:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    state: query
  delegate_to: localhost
  register: query_result
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        schema=dict(type='str', aliases=['name']),
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['schema']],
        ],
    )

    schema = module.params.get('schema')
    templates = module.params.get('templates')
    sites = module.params.get('sites')
    state = module.params.get('state')

    mso = MSOModule(module)

    schema_id = None
    path = 'schemas'

    # Query for existing object(s)
    if schema:
        mso.existing = mso.get_obj(path, displayName=schema)
        if mso.existing:
            schema_id = mso.existing.get('id')
            path = 'schemas/{id}'.format(id=schema_id)
    else:
        mso.existing = mso.query_objs(path)

    if state == 'query':
        pass

    elif state == 'absent':
        mso.previous = mso.existing
        if mso.existing:
            if module.check_mode:
                mso.existing = {}
            else:
                mso.existing = mso.request(path, method='DELETE')

    elif state == 'present':
        mso.previous = mso.existing

        payload = dict(
            id=schema_id,
            displayName=schema,
        )

        mso.sanitize(payload, collate=True)

        if mso.existing:
            if mso.check_changed():
                if module.check_mode:
                    mso.existing = mso.proposed
                else:
                    mso.existing = mso.request(path, method='PUT', data=mso.sent)
        else:
            if module.check_mode:
                mso.existing = mso.proposed
            else:
                mso.existing = mso.request(path, method='POST', data=mso.sent)

    mso.exit_json()


if __name__ == "__main__":
    main()

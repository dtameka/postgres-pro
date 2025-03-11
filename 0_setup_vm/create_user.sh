#!/bin/bash

ansible-playbook -i 0_setup_vm/hosts -u root 0_setup_vm/ansible-setup/add-users.yml
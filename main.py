import os
from flask import jsonify
import requests
import random

import numpy as numpy
from proxmoxer import ProxmoxAPI
from flask import Flask, send_from_directory
from flask import request
from flask_cors import CORS

proxmox_ip = '192.168.200.1'
proxmox_password = 'Geheim123!'
proxmox_node = 'pve'
proxmox_iso_storage = 'local'
default_password_for_new_accounts = "test1234!"

vlan_tag_file_name = 'vlantags.txt'
lowest_vlan_tag = 100
highest_vlan_tag = 300

proxmox = ProxmoxAPI(f'{proxmox_ip}:8006', user='root@pam',
                     password=proxmox_password, verify_ssl=False)

app = Flask(__name__, static_folder='ui/build')
CORS(app)


@app.route("/create-vm", methods=['POST'])
def create():
    if request.method == 'POST':
        print('===================incoming request=====================')
        data = request.get_json()
        user_data = data['users']
        vm_data = data['vms']
        pool = data['pool']
        print('pool: =============' + pool + '=====================')
        create_pool(pool)
        for group in user_data:
            group_name = random_group_name()
            print('group: ==============' + group_name + '=====================')
            create_group(group_name)
            vlan_tag = next_vlan_tag()

            for vm in vm_data:
                vmid = next_id()
                create_vm(
                    vmid=vmid,
                    name=vm['name'],
                    memory=vm['ram'],
                    sockets=vm['cpuSockets'],
                    cores=vm['cpuCores'],
                    iso=vm['iso'],
                    hdd_size=vm['hardDiskSize'],
                    vlan_tag=vlan_tag,
                    pool=pool
                )
                give_group_access_to_vm(group_name, vmid)

            for user in group:
                userid = user + '@pve'
                if not user_exists(userid):
                    create_user(userid, default_password_for_new_accounts, group_name)
                else:
                    add_user_to_group(userid, group_name)
        return 'see Flask console for logging'


@app.route("/available-iso", methods=['GET'])
def available_isos():
    if request.method == 'GET':
        return jsonify(get_available_iso_images())


@app.route("/available-pools", methods=['GET'])
def available_pools():
    if request.method == 'GET':
        return jsonify(get_available_pools())


@app.route("/pool", methods=['DELETE'])
def delete_pools():
    data = request.get_json()
    poolid = data['poolid']
    if request.method == 'DELETE':
        delete_vms(poolid)
        proxmox.pools(poolid).delete()
    return 'success'


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


def next_id():
    try:
        return int(proxmox.cluster.nextid.get())
    except Exception as e:
        print('API failure encountered.  %s' % str(e))
        return 0


def create_group(groupid):
    try:
        proxmox.access.groups.create(groupid=groupid)
        print(f'Proxmox PVE Created Group {groupid}')
    except Exception as e:
        print(f'API failure encountered {e}')


def create_pool(pool):
    try:
        proxmox.pools.create(poolid=pool)
        print(f'Proxmox PVE Created POOL {pool}')
    except Exception as e:
        print(f'API failure encountered {e}')


def add_user_to_group(userid, groupid):
    try:
        proxmox.access.users(userid).put(groups=groupid)
        print(f'Proxmox PVE Added User {userid} to group {groupid}')
    except Exception as e:
        print(f'API failure encountered {e}')


def create_user(userid, password, group):
    try:
        proxmox.access.users.create(userid=userid, password=password, groups=group)
        print(f'Proxmox PVE Created User {userid}')
    except Exception as e:
        print(f'API failure encountered {e}')


def give_user_access_to_vm(userid, vmid):
    try:
        proxmox.access.acl.put(path=f'/vms/{vmid}', users=f'{userid}@pve', roles="PVEAdmin")
        print(f'Gave {userid} access to vm {vmid}')
    except Exception as e:
        print(f'API failure encountered {e}')


def create_vm(vmid, name, memory, sockets, cores, iso, hdd_size, vlan_tag, pool):
    try:
        proxmox.nodes(proxmox_node).qemu.create(
            vmid=vmid,
            name=name,
            memory=memory,
            sockets=sockets,
            cores=cores,
            storage="local-lvm",
            onboot=0,
            ide2=f'file={iso},media=cdrom',
            scsihw="virtio-scsi-pci",
            scsi0=f'file=local-lvm:{hdd_size}',
            net0=f'model=virtio,bridge=vmbr2,tag={vlan_tag}',
            agent="1",
            pool=pool
        )
        print(f'Created vm {vmid} - {name}')
    except Exception as e:
        print(f'API failure encountered {e}')


def give_group_access_to_vm(groupid, vmid):
    try:
        proxmox.access.acl.put(path=f'/vms/{vmid}', groups=f'{groupid}', roles="PVEAdmin")
        print(f'Gave {groupid} access to vm {vmid}')
    except Exception as e:
        print(f'API failure encountered {e}')


def next_vlan_tag():
    if not os.path.exists(vlan_tag_file_name):
        open(vlan_tag_file_name, "w")

    f = open(vlan_tag_file_name, "r")
    data = f.read()
    if data == '':
        f = open(vlan_tag_file_name, "a")
        f.write(str(lowest_vlan_tag))
        f.close()
        return lowest_vlan_tag
    else:
        ids = [int(numeric_string) for numeric_string in data.split('\n')]
        highest = numpy.max(ids)
        nextid = highest + 1
        if nextid > highest_vlan_tag:
            return print('no vlan available')
        f = open(vlan_tag_file_name, "a")
        f.write('\n' + str(nextid))
        f.close()
        return nextid


def clone_and_edit(clone_id, new_id, vlan):
    node = proxmox.proxmox_node
    node.qemu(clone_id).clone.create(
        newid="%s" % new_id,
    )
    node.qemu(new_id).config.create(
        net0="model=virtio,bridge=vmbr2,tag=%s" % vlan
    )


def get_available_iso_images():
    iso = proxmox.nodes(proxmox_node).storage(proxmox_iso_storage).content.get(content='iso')
    return iso


def get_available_pools():
    pools = proxmox.pools.get()
    return pools


def random_group_name():
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site)
    words = response.content.splitlines()
    return random.choice(words).decode("utf-8") + random.choice(words).decode("utf-8")


def user_exists(user):
    try:
        proxmox.access.users(user).get()
        return True
    except Exception as e:
        return False


def delete_vms(pool):
    try:
        test = proxmox.pools(pool).get()
        vms = test['members']
        vmids = list(map(lambda vm: vm['vmid'], vms))
        print(vmids)
        for vmid in vmids:
            proxmox.nodes(proxmox_node).qemu(vmid).delete()
            print(f'Delete vm {vmid}')
    except Exception as e:
        print(f'API failure encountered {e}')


if __name__ == '__main__':
    app.run(use_reloader=True, port=5000, threaded=True)


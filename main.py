import os

from proxmoxer import ProxmoxAPI
from flask import Flask, send_from_directory
from flask import request
from flask_cors import CORS

proxmox_ip = '192.168.100.2'
proxmox_password = 'Geheim123!'
proxmox_node = 'my'
default_password_for_new_accounts = "test1234!"

proxmox = ProxmoxAPI(f'{proxmox_ip}:8006', user='root@pam',
                     password='Geheim123!', verify_ssl=False)

app = Flask(__name__, static_folder='ui/build')
CORS(app)


@app.route("/create", methods=['POST'])
def create():
    if request.method == 'POST':
        data = request.get_json()
        userid = data["userid"]
        create_vm_for_new_user(userid)
        return f'created vm for user {userid}'

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
    except Exception as e:
        print(f'API failure encountered {e}')
    print(f'Proxmox PVE Created Group {groupid}')


def add_user_to_group(userid, groupid):
    username = userid + '@pve'
    try:
        proxmox.access.users(username).put(groups=groupid)
    except Exception as e:
        print(f'API failure encountered {e}')
    print(f'Proxmox PVE Added User {userid} to group {groupid}')


def create_user(userid, password, group):
    username = userid + '@pve'
    try:
        if group is not None:
            proxmox.access.users.create(userid=username, password=password, groups=group)
        else:
            proxmox.access.users.create(userid=username, password=password)
    except Exception as e:
        print(f'API failure encountered {e}')
    print(f'Proxmox PVE Created User {userid}')


def give_user_access_to_vm(userid, vmid):
    try:
        proxmox.access.acl.put(path=f'/vms/{vmid}', users=f'{userid}@pve', roles="PVEAdmin")
    except Exception as e:
        print(f'API failure encountered {e}')
    print(f'Gave {userid} access to vm {vmid}')


def create_vm(vmid):
    try:
        proxmox.nodes(proxmox_node).qemu.create(
            vmid=vmid,
            name="bootstrap",
            memory=16368,
            sockets=2,
            cores=2,
            storage="local-lvm",
            onboot=0,
            ide2="file=iso:iso/CentOS-8.3.2011-aarch64-boot.iso,media=cdrom",
            scsihw="virtio-scsi-pci",
            scsi0="file=local-lvm:120",
            net0="model=virtio,bridge=vmbr0"
        )
    except Exception as e:
        print(f'API failure encountered {e}')
    print(f'Created vm {vmid}')


def add_group_to_vm(groupid, vmid):
    try:
        proxmox.access.acl.put(path=f'/vms/{vmid}', groups=f'{groupid}', roles="PVEAdmin")
    except Exception as e:
        print(f'API failure encountered {e}')
    print(f'Gave {groupid} access to vm {vmid}')


def create_vm_for_new_user(userid):
    vmid = next_id();
    create_user(userid=userid, password=default_password_for_new_accounts)
    create_vm(vmid)
    give_user_access_to_vm(userid=userid, vmid=vmid)


def create_vm_for_new_user_and_put_in_group(userid, group):
    vmid = next_id();
    create_user(userid=userid, password=default_password_for_new_accounts, group=group)
    create_vm(vmid)
    give_user_access_to_vm(userid=userid, vmid=vmid)


if __name__ == '__main__':
    app.run(use_reloader=True, port=5000, threaded=True)


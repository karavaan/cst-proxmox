from proxmoxer import ProxmoxAPI

proxmox_ip = '192.168.100.2'
proxmox_password = 'Geheim123!'
proxmox_node = 'my'
default_password_for_new_accounts = "test1234!"

proxmox = ProxmoxAPI(f'{proxmox_ip}:8006', user='root@pam',
                     password='Geheim123!', verify_ssl=False)


def next_id():
    try:
        return int(proxmox.cluster.nextid.get())
    except Exception as e:
        print('API failure encountered.  %s' % str(e))
        return 0


def create_user(userid, password):
    username = userid + '@pve'
    try:
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


def create_vm_for_new_user(userid):
    vmid = next_id();
    create_user(userid=userid, password=default_password_for_new_accounts)
    create_vm(vmid)
    give_user_access_to_vm(userid=userid, vmid=vmid)


if __name__ == '__main__':
    create_vm_for_new_user('pop')

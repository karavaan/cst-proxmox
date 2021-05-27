import os

from proxmoxer import ProxmoxAPI

proxmox = ProxmoxAPI('192.168.100.2:8006', user='root@pam',
                     password='Geheim123!', verify_ssl=False)


def print_vms():
    for vm in proxmox.cluster.resources.get(type='vm'):
        print("{0}. {1} => {2}".format(vm['vmid'], vm['name'], vm['status']))



def create_vm():
    node = proxmox.nodes('my')
    print(node)
    node.qemu.create(
        vmid=332,
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_vm()
    print_vms()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

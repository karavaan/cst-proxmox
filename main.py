from proxmoxer import ProxmoxAPI

proxmox = ProxmoxAPI('192.168.100.2:8006', user='root@pam',
                     password='Geheim123!', verify_ssl=False)


def print_vms():
    for vm in proxmox.cluster.resources.get(type='vm'):
        print("{0}. {1} => {2}".format(vm['vmid'], vm['name'], vm['status']))


def create_vm():
    node = proxmox.nodes('my')
    print(node)
    node.lxc.create(vmid=205,
                    ostemplate='',
                    hostname='debian-stretch',
                    storage='local-lvm',
                    memory=512,
                    swap=512,
                    cores=1,
                    password='secret',
                    net0='name=eth0,bridge=vmbr0,ip=192.168.22.1/20,gw=192.168.16.1')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_vm()
    print_vms()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

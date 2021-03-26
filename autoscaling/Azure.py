from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os

class Azure:
    def __init__(self):
        self.set_Azure_credentials()
        self.create_Azure_clients()
        self.resource_group = os.environ['RESOURCE_GROUP']

    # Set the Azure credential using the pre-generated Service Principal
    def set_Azure_credentials(self):
        self.subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
        self.credentials = ServicePrincipalCredentials(
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant=os.environ['AZURE_TENANT_ID']
        )

    # Create all clients with an Application (service principal) token provider
    def create_Azure_clients(self):
        self.resource_client = ResourceManagementClient(self.credentials, self.subscription_id)
        self.compute_client = ComputeManagementClient(self.credentials, self.subscription_id)
        self.network_client = NetworkManagementClient(self.credentials, self.subscription_id)

    # Return a list with the deployed Virtual Machines under self.resource_group Resource Group
    def get_deployed_vms(self):
        return self.compute_client.virtual_machines.list(self.resource_group)

    def delete_vms(self, vms_numbers):
        for vm_number in vms_numbers:
            vm_name = "Worker"+str(vm_number)
            nic_name = vm_name+"VMNic"
            nsg_name = vm_name+"NSG"
            ip_name = vm_name+"PublicIP"

            # Delete VM
            print('Delete VM {}'.format(vm_name))
            print('Delete NIC {}'.format(nic_name))
            try:
                async_vm_delete = self.compute_client.virtual_machines.delete(self.resource_group, vm_name)
                async_vm_delete.wait()
                net_del_poller = self.network_client.network_interfaces.delete(self.resource_group, nic_name)
                net_del_poller.wait()
                # Wait until the Network Interface is deleted to proceed
                while(not net_del_poller.done()):
                    sleep(5)
                async_nsg = self.network_client.network_security_groups.delete(self.resource_group, nsg_name)
                async_nsg.wait()
                async_ip = self.network_client.public_ip_addresses.delete(self.resource_group, ip_name)
                async_ip.wait()
                disks_list = self.compute_client.disks.list_by_resource_group(self.resource_group)
                disk_handle_list = []
                for disk in disks_list:
                    if vm_name in disk.name:
                        print('Delete Disk {}'.format(disk.name))
                        async_disk_delete = self.compute_client.disks.delete(self.resource_group, disk.name)
                        disk_handle_list.append(async_disk_delete)
                print("Queued disks will be deleted now...")
                for async_disk_delete in disk_handle_list:
                    async_disk_delete.wait()
            except CloudError:
                print('A VM delete operation failed: {}'.format(traceback.format_exc()))
            print("Deleted VM {}".format(vm_name))

"""Create and manage virtual machines.
This script expects that the following environment vars are set:
AZURE_TENANT_ID: your Azure Active Directory tenant id or domain
AZURE_CLIENT_ID: your Azure Active Directory Application Client ID
AZURE_CLIENT_SECRET: your Azure Active Directory Application Secret
AZURE_SUBSCRIPTION_ID: your Azure Subscription Id
"""
import subprocess
import os
import CitusCluster
import Azure
from kubernetes import client, config

class K8sCluster:

    def __init__(self, minimum_vms, maximum_vm):
        # Configs can be set in Configuration class directly or using helper utility
        config.load_kube_config()
        self.k8s = client.CoreV1Api()

        self.AZUREPASSWORD = os.environ['AZURE_PASSWORD']

        self.minimum_vms = minimum_vms
        self.maximum_vm = maximum_vm

        self.azure = Azure.Azure()
        self.COORDIP = self.get_coordinator_ip()
        self.citus_cluster = CitusCluster.CitusCluster(self.COORDIP)


    # Add vm_to_create number of VMs to the existing Kubernetes cluster
    def cluster_scale_out(self, vm_to_create):
        vm_list = self.azure.compute_client.virtual_machines.list("ClusterGroup")
        max_worker_name = 0
        vm_name_list = []

        # Get the current number of Worker nodes
        for vm in vm_list:
            if(vm.name != "Coordinator"):
                if(len(vm.name.split("Worker")) == 2 and vm.name.split("Worker")[1].isnumeric() and int(vm.name.split("Worker")[1]) > max_worker_name):
                    max_worker_name = int(vm.name.split("Worker")[1])
                    vm_name_list.append(int(vm.name.split("Worker")[1]))

        # Decide whether more VMs can be added
        if (len(vm_name_list) + vm_to_create <= self.maximum_vm):
            print("creating "+str(vm_to_create) + "VMs")
            # Call the addNewVms.sh bash script to deploy vm_to_create number of VMs
            rc = subprocess.check_call(['./scripts/addNewVms.sh', self.AZUREPASSWORD, str(max_worker_name + 1), str(max_worker_name + vm_to_create), str(max_worker_name + vm_to_create - 1)])
        # If the maximum number of VMs will be exceeded, modify the number of VMs to be added
        else:
            vm_to_create = self.maximum_vm - len(vm_name_list)
            if (vm_to_create > 0):
                print("creating " + str(vm_to_create) + "VMs")
                # Call the addNewVms.sh bash script to deploy vm_to_create number of VMs
                rc = subprocess.check_call(['./scripts/addNewVms.sh', self.AZUREPASSWORD, str(max_worker_name + 1), str(max_worker_name + vm_to_create), str(max_worker_name + vm_to_create -1)])


    def cluster_scale_in(self, vm_to_delete):
        vm_list = self.azure.compute_client.virtual_machines.list("ClusterGroup")
        vm_name_list = []

        # Append all the Worker names in a list
        for vm in vm_list:
            if (vm.name != "Coordinator"):
                if (len(vm.name.split("Worker")) == 2 and vm.name.split("Worker")[1].isnumeric()):
                    vm_name_list.append(int(vm.name.split("Worker")[1]))

        # Decide whether there are enough VMs to remove
        if(len(vm_name_list) - vm_to_delete >= self.minimum_vms):
            remove_flag = True
        # If there are not enough VMs to delete, delete vm_to_delete VMs to reach the minimum accepted
        # number of VMs (self.minimum_vms)
        else:
            vm_to_delete = len(vm_name_list) - self.minimum_vms
            if(vm_to_delete > 0):
                remove_flag = True

        if(remove_flag):
            # Sort the list in descending order
            vm_name_list.sort(reverse=True)
            for i in range(vm_to_delete):
                worker_ip = self.get_pod_internal_ip(i)
                self.citus_cluster.delete_node(worker_ip)

    # Return Coordinator's VM public ip address
    def get_coordinator_ip(self):
        ip_addresses = self.azure.network_client.public_ip_addresses.list("ClusterGroup")
        for ip in ip_addresses:
            if(ip.name == "CoordinatorPublicIP"):
                return ip.ip_address

    # Return worker_name's public ip address
    def get_worker_ip(self, worker_name):
        ip_addresses = self.azure.network_client.public_ip_addresses.list("ClusterGroup")
        for ip in ip_addresses:
            if(ip.name == worker_name+"PublicIP"):
                return ip.ip_address


    # Return the ip of the pod with name citus-worker-[worker_num]
    def get_pod_internal_ip(self, worker_num):
        print("Listing pods with their IPs:")
        ret = self.k8s.list_pod_for_all_namespaces(watch=False)
        for pod in ret.items:
            print(pod.metadata.name)
            if(pod.metadata.name == "citus-worker-"+str(worker_num)):
                print(pod.status.pod_ip)



#cluster_scale_out(compute_client, 2)


cluster = K8sCluster(1,10)
cluster.cluster_scale_out(1)
#citusCluster.get_pod_internal_ip(0)
#citusCluster.cluster_scale_in(12)

# MobilityDB-in-Azure


## Execution Guidelines

The purpose of this section is to enable the user reuse the existing work.

### Required Components
This work combines different tools and technologies to create a self-managed database on the cloud. The following list include the required components along with some links that assist the users install and configure them.

* A local computer running **Linux OS** (tested with Ubuntu 20.04).
* A **Microsoft Azure account** with an active subscription attached to it. The user must have full access to the Azure resources (Owner).
* A Service Principal, created and configured for your Azure account. More details on how to create a Service Principal can be found [here](https://docs.microsoft.com/en-us/azure/developer/python/configure-local-development-environment?tabs=cmd#required-components).

### Cluster Initialization
To deploy a MobilityDB cluster on Azure, follow the below steps:
<ol>
<li>Clone the Github repository</li>
<li>Configure the bash script under the path <strong>MobilityDB-in-Azure/automaticClusterDeployment/KubernetesCluster/deployK8SCluster.sh</strong>, by modifying the values of the parameters placed on the top of the file in the following way:
    <ul>
    <li><code>AzureUsername</code> parameter is used to login to your Azure account.</li>
    <li>The default <code>ResourceGroupName</code>, <code>Location</code> and <code>VirtualNetwork</code> values can be used.</li>
    <li><code>Subscription</code> defines the name of the active Azure subscription.</li>
    <li><code>VMsNumber</code> determines the number of Worker nodes and <code>VMsSize</code> the size of each machine</li>
    <li><code>SSHPublicKeyPath</code> and <code>SSHPrivateKeyPath</code> values specify the location of the ssh private and public keys to access the created VMs. By default, the files will be stored in <strong>~/.ssh/</strong> directory.</li>
    <li><code>Gitrepo</code> specifies the Github repository from which the installation scripts and the rest source files will be found.</li>
    <li><code>Service_app_url</code> determines  the  url  of  the  Service  Principal  and <code>Service_tenant</code> the tenant’s id. When executing the script, the <code>Client secret</code> should be given by the user to authenticate the application in Azure.</li>
    </ul>
</li>
<li>Execute the script by running <code>bash MobilityDB-in-Azure/automaticClusterDeployment/KubernetesCluster/deployK8SCluster.sh</code>. fter some few minutes, the cluster will be deployed on Azure.</li>
</ol>

When the cluster is ready, you can access any machine using the `~/.ssh/id_rsa` key. The next step is to establish an ssh connection to the Coordinator VM. To connect to the machine, run `ssh -i ~/.ssh/id_rsa azureuser@{vm_ip_address}`, where vm_ip_address is the public ip address of the Coordinator VM that can be found inAzure portal. When connected to the VM, you can confirm that the K8S cluster has been successfully initialized by executing `sudo kubectl get nodes`.

### Deploying A PostgreSQL Cluster

Until now we have created a Kubernetes cluster on Azure. The purpose of this section is to deploy a PostgreSQL cluster with Citus and MobilityDB extensions installed. First we need to modify the provided configuration files:
<ol>
<li>Edit the content of <strong>MobilityDB-in-Azure/KubernetesDeployment/postgres-secrets-params.yaml</strong> file by changing the values of the <strong>username</strong> and <strong>password</strong>.These credentials will be the default keys to access the PostgreSQL server.  The values should be provided as base64-encoded strings. To get such an encoding, you can use the following shell command: <code>echo -n "postgres" | base64</code>.</li>
<li>Replace the content of the folder <strong>MobilityDB-in-Azure/KubernetesDeployment/secrets</strong> by creating your own SSL certificate that Citus will use to encrypt the database data.</li>
<li>Edit the content of <strong>MobilityDB-in-Azure/KubernetesDeployment/postgres-deployment-workers.yaml</strong> by setting the replicas to be equal to the number of available worker machines.</li>
</ol>

Now you are ready to connect to your distributed PostgreSQL cluster. After connecting to the Coordinator VM, execute the following shell command to ensure that the Pods are running, as show in the following screenshot : `sudo kubectl get pods -o wide`. Normally, you should see one Pod hosting the citus-master and a number of citus-worker Pods, equal to the replica number that you defined before.<br><br>

![alt text](readme images/pods_screenshot.png)

You can connect to the Citus Coordinator by using the **public ip** of the master VM as **host name/address**, **30001 as port**, **postgres as database** and the **username** and **password** that you defined before. The default values are **postgresadmin** and **admin1234**, respectively. Try to execute some Citus or MobilityDB queries. For instance, run `select master_get_active_worker_nodes()` to view the available Citus worker nodes.



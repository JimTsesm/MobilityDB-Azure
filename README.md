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
<li>Execute the bash script by running <code>bash MobilityDB-in-Azure/automaticClusterDeployment/KubernetesCluster/deployK8SCluster.sh</code>. **Before running the script**, the parameters placed on the top of the file needs to be configured as follows:
    <ul>
    <li><code>AzureUsername</code> parameter is used to login to your Azure account.</li>
    <li>The default <code>ResourceGroupName</code>,<code>Location</code> and <code>VirtualNetwork</code> values can be used.</li>
    <li><code>Subscription</code> defines the name of the active Azure subscription.</li>
    <li><code>VMsNumber</code> determines the number of Worker nodes and <code>VMsSize</code> the size of each machine</li>
    <li><code>SSHPublicKeyPath</code> and <code>SSHPrivateKeyPath</code> values specify the location of the ssh private and public keys to access the created VMs. By default, the files will be stored in **~/.ssh/** directory.</li>
    <li><code>Gitrepo</code> specifies the Github repository from which the installation scripts and the rest source files will be found.</li>
    <li><code>Service_app_url</code> determines  the  url  of  the  Service  Principal  and <code>Service_tenant</code> the tenant’s id. When executing the script, the <code>Client secret</code> should be given by the user to authenticate the application in Azure.</li>
    </ul>
</li>
</ol>



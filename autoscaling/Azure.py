from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os

class Azure:
    def __init__(self):
        self.set_Azure_credentials()
        self.create_Azure_clients()

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

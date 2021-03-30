import time
import logging
import os
import argparse
import utils
from K8sCluster import K8sCluster

from daemons.prefab import run


class AutoscalingDaemon(run.RunDaemon):

    def __init__(self, pidfile, minvm, maxvm, storage_path, metric, observations_interval):
        super().__init__(pidfile=pidfile)
        self.minvm = minvm
        self.maxvm = maxvm
        self.metric = metric
        self.observations_interval = observations_interval
        self.storage_path = storage_path

    def monitor(self):
        return self.k8s_cluster.azure.monitor.get_azure_metric(metric=self.metric, interval=self.observations_interval)

    def analyze(self, vms_observations):
        # For each VM
        for vm_name in vms_observations.keys():
            vm_average_metric = utils.list_average(vms_observations[vm_name])
            logging.info(vm_average_metric)

    def run(self):

        # Daemon restarted
        if (os.path.exists(self.storage_path)):
            logging.info("Continuing from a past state...")

        # Daemon initialized for the first time
        else:
            logging.info("Starting new state")
            os.mkdir(self.storage_path)
        # to be handled according to start/restart
        self.k8s_cluster = K8sCluster(self.minvm, self.maxvm)
        # Run Daemon's job
        while True:
            self.analyze(self.monitor())
            time.sleep(10)



if __name__ == '__main__':

    # Parse the input arguments
    parser = argparse.ArgumentParser(description='Reading Auto-scaling arguments.')
    parser.add_argument('--action', dest='action', required=True, choices=['start', 'stop', 'restart'],
                        help='available auto-scaling daemon actions: {start, stop, restart}')
    parser.add_argument('--minvm', dest='minvm', required=True,
                        help='Minimum number of Worker VMs.')
    parser.add_argument('--maxvm', dest='maxvm', required=True,
                        help='Maximum number of Worker VMs.')
    parser.add_argument('--storage', dest='storage_path', required=True,
                        help='Specify a storage path.')
    args = parser.parse_args()

    # Check if range arguments are correct
    utils.range_type(args.minvm, args.maxvm)

    # Configure the logging
    logging.basicConfig(filename='/var/run/autoscaling.log', level=logging.INFO, filemode='a',
                        format='[%(asctime)s] - %(levelname)s - %(message)s')
    pidfile = os.path.join(os.getcwd(), "/var/run/autoscaling.pid")

    d = AutoscalingDaemon(pidfile, args.minvm, args.maxvm, args.storage_path, metric="Percentage CPU", observations_interval=10)

    # Decide which Daemon action to do
    if args.action == "start":
        d.start()
    elif args.action == "stop":
        d.stop()
    elif args.action == "restart":
        d.restart()
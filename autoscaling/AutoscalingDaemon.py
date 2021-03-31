import time
import logging
import os
import argparse
import utils
from K8sCluster import K8sCluster

from daemons.prefab import run


class AutoscalingDaemon(run.RunDaemon):

    def __init__(self, pidfile, performance_logger, minvm, maxvm, storage_path, lower_threshold, upper_threshold, metric, observations_interval):
        super().__init__(pidfile=pidfile)
        self.minvm = minvm
        self.maxvm = maxvm
        self.metric = metric
        self.observations_interval = observations_interval
        self.storage_path = storage_path
        self.performance_logger = performance_logger
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

    # Get the specified metric provided by Azure at VM level.
    def monitor(self):
        return self.k8s_cluster.azure.monitor.get_azure_metric(metric=self.metric, interval=self.observations_interval)

    # Receive the metrics computed by the monitor phase and compute the average metric of each VM.
    def analyze(self, vms_observations):
        vms_average = []
        vote_to_scale_out = 0
        vote_to_scale_in = 0
        vote_nothing = 0

        # For each VM compute the average metric of the past observations_interval observations
        for vm_name in vms_observations.keys():
            vm_average_metric = utils.list_average(vms_observations[vm_name], tuple_list=True)
            if(vm_average_metric > self.upper_threshold):
                vote_to_scale_out += 1
            elif(vm_average_metric < self.lower_threshold):
                vote_to_scale_in += 1
            else:
                vote_nothing += 1
            vms_average.append(vm_average_metric)
            self.performance_logger.info(vm_average_metric)

        return vote_to_scale_out, vote_to_scale_in, vote_nothing, vms_average

    def plan(self, vote_to_scale_out, vote_to_scale_in, vote_nothing, vms_average):
        # Scale out according to votes
        if(vote_to_scale_out > vote_to_scale_in and vote_to_scale_out > vote_nothing):
            self.performance_logger.info("Scaling out...")
        # Scale in according to votes
        elif(vote_to_scale_out < vote_to_scale_in and vote_to_scale_in > vote_nothing):
            self.performance_logger.info("Scaling in...")
        # If no decision can be taken according to votes, compute the global average metric
        else:
            global_average = utils.list_average(vms_average)
            if(global_average > self.upper_threshold):
                self.performance_logger.info("Scaling out 2...")
            elif(global_average < self.lower_threshold):
                self.performance_logger.info("Scaling in 2...")
            else:
                self.performance_logger.info("Do nothing...")
    
    def enter_cool_down_period(self, minutes):
        self.performance_logger.info("Entering to cool down period for "+str(minutes)+" minutes")
        time.sleep(minutes * 60)
        self.performance_logger.info("Exciting from cool down period")

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
            vote_to_scale_out, vote_to_scale_in, vote_nothing, vms_average = self.analyze(self.monitor())
            self.plan(vote_to_scale_out, vote_to_scale_in, vote_nothing, vms_average)
            time.sleep(self.observations_interval * 60)



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
    parser.add_argument('--lower_th', dest='lower_threshold', required=True,
                        help='Specify the lower threshold for the metric.')
    parser.add_argument('--upper_th', dest='upper_threshold', required=True,
                        help='Specify the upper threshold for the metric.')
    args = parser.parse_args()

    # Check if range arguments are correct
    utils.range_type(args.minvm, args.maxvm, 0)
    utils.range_type(args.lower_threshold, args.upper_threshold, 0, 100)

    performance_logger = utils.setup_loggers()

    # Get Daemon PID
    pidfile = os.path.join(os.getcwd(), "/var/run/autoscaling.pid")

    d = AutoscalingDaemon(pidfile, performance_logger, int(args.minvm), int(args.maxvm),
                          args.storage_path, int(args.lower_threshold), int(args.upper_threshold),
                          metric="Percentage CPU", observations_interval=3
                          )

    # Decide which Daemon action to do
    if args.action == "start":
        d.start()
    elif args.action == "stop":
        d.stop()
    elif args.action == "restart":
        d.restart()
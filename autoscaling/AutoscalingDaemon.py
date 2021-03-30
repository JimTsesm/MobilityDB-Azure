import time
import logging
import os
import sys
import argparse
import utils

from daemons.prefab import run


class AutoscalingDaemon(run.RunDaemon):

    def run(self):
        if (os.path.exists("/home/dimitris/Desktop/thesis/MobilityDB-in-Azure/autoscaling/test_dir")):
            logging.info("Continuing from a past state...")
        else:
            logging.info("Starting new state")
            os.mkdir("/home/dimitris/Desktop/thesis/MobilityDB-in-Azure/autoscaling/test_dir")
        while True:
            logging.info('do something.......')
            time.sleep(1)

if __name__ == '__main__':

    # Parse the input arguments
    parser = argparse.ArgumentParser(description='Reading Auto-scaling arguments.')
    parser.add_argument('--action', dest='action', required=True, choices=['start', 'stop', 'restart'],
                        help='available auto-scaling daemon actions: {start, stop, restart}')
    parser.add_argument('--minvm', dest='minvm', required=True,
                        help='Minimum number of Worker VMs.')
    parser.add_argument('--maxvm', dest='maxvm', required=True,
                        help='Maximum number of Worker VMs.')
    args = parser.parse_args()

    # Check if range arguments are correct
    utils.range_type(args.minvm, args.maxvm)

    # Configure the logging
    logging.basicConfig(filename='/var/run/autoscaling.log', level=logging.INFO, filemode='a',
                        format='[%(asctime)s] - %(levelname)s - %(message)s')
    pidfile = os.path.join(os.getcwd(), "/var/run/autoscaling.pid")

    d = AutoscalingDaemon(pidfile=pidfile)

    # Decide which Daemon action to do
    if args.action == "start":
        d.start()
    elif args.action == "stop":
        d.stop()
    elif args.action == "restart":
        d.restart()
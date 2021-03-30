import os

import psycopg2

class CitusCluster:
    def __init__(self, coordinator_ip):
        self.POSTGREDB = os.environ['POSTGREDB']
        self.POSTGREUSER = os.environ['POSTGREUSER']
        self.POSTGREPASSWORD = os.environ['POSTGREPASSWORD']
        self.POSTGREPORT = os.environ['POSTGREPORT']
        self.COORDIP = coordinator_ip
        # Establish connection with the Citus Coordinator
        self.connection = psycopg2.connect(database=self.POSTGREDB, user=self.POSTGREUSER, password=self.POSTGREPASSWORD, host=self.COORDIP,
                               port=self.POSTGREPORT)
        print("Database opened successfully")

    def delete_node(self, nodes_ip):
        cur = self.connection.cursor()

        for node_ip in nodes_ip:
            # Mark the worker node with node_ip to be deleted
            cur.execute("SELECT * FROM citus_set_node_property('%s', 5432, 'shouldhaveshards', false)" % node_ip)

        # Drain all the marked node at once
        cur.execute("SELECT * FROM rebalance_table_shards(drain_only := true)")

        # Remove the nodes from the Cluster
        for node_ip in nodes_ip:
            cur.execute("SELECT master_remove_node('%s', 5432)" % node_ip)

        # Commit the transaction
        self.connection.commit()

import psycopg2

class CitusCluster:
    def __init__(self, coordinator_ip):
        self.POSTGREDB = "postgres"
        self.POSTGREUSER = "postgresadmin"
        self.POSTGREPASSWORD = "admin1234"
        self.POSTGREPORT = "31996"
        self.COORDIP = coordinator_ip
        # Establish connection with the Citus Coordinator
        self.connection = psycopg2.connect(database=self.POSTGREDB, user=self.POSTGREUSER, password=self.POSTGREPASSWORD, host=self.COORDIP,
                               port=self.POSTGREPORT)
        print("Database opened successfully")

    def delete_node(self, node_ip):
        cur = self.connection.cursor()
        # Delete the Citus shards from the target node
        print("DELETE from pg_dist_shard_placement where nodename = '%s' and nodeport = 5432;", node_ip)
        #cur.execute("DELETE from pg_dist_shard_placement where nodename = '%s' and nodeport = 5432", node_ip)
        # Remove the node from the Cluster
        #cur.execute("SELECT master_remove_node('%s', 5432)",node_ip)
        # Re-balance table shards to assure the replication factor
        #cur.execute("SELECT rebalance_table_shards()")
        # con.commit()

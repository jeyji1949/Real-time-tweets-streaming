from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
session = cluster.connect("realtime")

rows = session.execute("SELECT * FROM tweets")

for row in rows:
    print(row)

cluster.shutdown()

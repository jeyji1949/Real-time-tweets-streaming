# Cassandra Storage

Handles tweet storage using Apache Cassandra.

Files:
- schema.cql : database schema
- cassandra_store.py : insert helper
- consumer_cassandra.py : Kafka consumer (future)
- test_cassandra.py : connection test

Run schema:
docker exec -it cassandra-db cqlsh -f schema.cql

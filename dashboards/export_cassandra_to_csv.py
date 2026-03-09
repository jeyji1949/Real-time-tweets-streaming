#!/usr/bin/env python3
"""
Exporte les données depuis Cassandra vers CSV
"""

from cassandra.cluster import Cluster
import csv
from datetime import datetime

class CassandraCSVExporter:
    def __init__(self, hosts=['127.0.0.1'], keyspace='twitter_analytics'):
        cluster = Cluster(hosts)
        self.session = cluster.connect(keyspace)
    
    def export_all_tweets(self, filename=None, limit=10000):
        """Exporte tous les tweets depuis Cassandra"""
        if filename is None:
            filename = f"cassandra_tweets_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Requête (ATTENTION : peut être lente)
        query = f"SELECT * FROM tweets LIMIT {limit}"
        rows = self.session.execute(query)
        
        fieldnames = [
            'tweet_id', 'text', 'user', 'lang', 'created_at', 'indexed_at',
            'sentiment', 'confidence', 'score', 'topic',
            'hashtags', 'retweet_count', 'like_count', 'analysis_method'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            count = 0
            for row in rows:
                # Convertir Row en dict
                row_dict = {
                    'tweet_id': row.tweet_id,
                    'text': row.text,
                    'user': row.user,
                    'lang': row.lang,
                    'created_at': row.created_at.isoformat() if row.created_at else '',
                    'indexed_at': row.indexed_at.isoformat() if row.indexed_at else '',
                    'sentiment': row.sentiment,
                    'confidence': row.confidence,
                    'score': row.score,
                    'topic': row.topic,
                    'hashtags': ', '.join(row.hashtags) if row.hashtags else '',
                    'retweet_count': row.retweet_count,
                    'like_count': row.like_count,
                    'analysis_method': row.analysis_method
                }
                
                writer.writerow(row_dict)
                count += 1
        
        print(f"✅ Export Cassandra réussi : {filename}")
        print(f"📊 {count} tweets exportés")
        
        return filename
    
    def export_by_topic(self, topic, filename=None, limit=1000):
        """Exporte les tweets d'un topic spécifique"""
        if filename is None:
            filename = f"cassandra_{topic}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        query = f"SELECT * FROM tweets_by_topic WHERE topic = '{topic}' LIMIT {limit}"
        rows = self.session.execute(query)
        
        fieldnames = ['topic', 'created_at', 'tweet_id', 'text', 'user', 'sentiment', 'confidence']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            count = 0
            for row in rows:
                writer.writerow({
                    'topic': row.topic,
                    'created_at': row.created_at.isoformat() if row.created_at else '',
                    'tweet_id': row.tweet_id,
                    'text': row.text,
                    'user': row.user,
                    'sentiment': row.sentiment,
                    'confidence': row.confidence
                })
                count += 1
        
        print(f"✅ Export topic '{topic}' : {filename}")
        print(f"📊 {count} tweets exportés")
        
        return filename


if __name__ == "__main__":
    exporter = CassandraCSVExporter()
    
    # Export complet
    print("📥 Export 1 : Tous les tweets")
    exporter.export_all_tweets(limit=1000)
    
    # Export par topic
    print("\n📥 Export 2 : Topic AI")
    exporter.export_by_topic('AI')
    
    print("\n📥 Export 3 : Topic Cloud")
    exporter.export_by_topic('Cloud')
    
    print("\n✅ Exports Cassandra terminés !")
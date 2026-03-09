#!/usr/bin/env python3
"""
Exporte les tweets depuis Elasticsearch vers CSV
"""

from fileinput import filename

from elasticsearch import Elasticsearch
import csv
from datetime import datetime
import sys

class ElasticsearchCSVExporter:
    def __init__(self, es_host='http://localhost:9200', index='tweets_index_improved'):
        self.es = Elasticsearch([es_host])
        self.index = index
    
    def export_all_tweets(self, filename=None, max_size=10000):
        """
        Exporte tous les tweets en CSV
        
        Args:
            filename: Nom du fichier (auto si None)
            max_size: Nombre max de tweets à exporter
        """
        if filename is None:
            filename = f"tweets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Query pour récupérer les tweets
        query = {
            "query": {"match_all": {}},
            "sort": [{"created_at": "desc"}],
            "size": min(max_size, 10000)  # ES limit
        }
        
        result = self.es.search(index=self.index, body=query)
        hits = result['hits']['hits']
        
        if not hits:
            print("⚠️  Aucun tweet à exporter")
            return None
        
        # Définir les colonnes
        fieldnames = [
            'tweet_id', 'text', 'user', 'lang', 'created_at',
            'sentiment', 'confidence', 'score', 'topic',
            'hashtags', 'retweet_count', 'like_count', 'analysis_method'
        ]
        
        # Écrire le CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            
            writer.writeheader()
            
            for hit in hits:
                tweet = hit['_source']
                
                # Formater les listes en string
                if 'hashtags' in tweet and isinstance(tweet['hashtags'], list):
                    tweet['hashtags'] = ', '.join(tweet['hashtags'])
                
                writer.writerow(tweet)
        
        print(f"✅ Export réussi : {filename}")
        print(f"📊 {len(hits)} tweets exportés")
        
        return filename
    
    def export_by_sentiment(self, sentiment, filename=None):
        """Exporte seulement un sentiment spécifique"""
        if filename is None:
            filename = f"tweets_{sentiment}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        query = {
            "query": {
                "term": {"sentiment.keyword": sentiment}
            },
            "sort": [{"created_at": "desc"}],
            "size": 10000
        }
        
        result = self.es.search(index=self.index, body=query)
        hits = result['hits']['hits']
        
        # Même logique que export_all_tweets
        fieldnames = [
            'tweet_id', 'text', 'user', 'created_at',
            'confidence', 'topic', 'hashtags', 'like_count'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for hit in hits:
                tweet = hit['_source']
                if 'hashtags' in tweet and isinstance(tweet['hashtags'], list):
                    tweet['hashtags'] = ', '.join(tweet['hashtags'])
                writer.writerow(tweet)
        
        print(f"✅ Export {sentiment} réussi : {filename}")
        print(f"📊 {len(hits)} tweets exportés")
        
        return filename
    
    def export_top_hashtags(self, filename=None, size=50):
        """Exporte les top hashtags en CSV"""
        if filename is None:
            filename = f"top_hashtags_{datetime.now().strftime('%Y%m%d')}.csv"
        
        query = {
            "size": 0,
            "aggs": {
                "top_hashtags": {
                    "terms": {
                        "field": "hashtags.keyword",
                        "size": size
                    }
                }
            }
        }
        
        result = self.es.search(index=self.index, body=query)
        buckets = result['aggregations']['top_hashtags']['buckets']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Rang', 'Hashtag', 'Nombre'])
            
            for i, bucket in enumerate(buckets, 1):
                writer.writerow([i, bucket['key'], bucket['doc_count']])
        
        print(f"✅ Export top hashtags : {filename}")
        print(f"📊 {len(buckets)} hashtags exportés")
        
        return filename
    
    def export_stats_by_topic(self, filename=None):
        """Exporte les stats par topic en CSV"""
        if filename is None:
            filename = f"stats_by_topic_{datetime.now().strftime('%Y%m%d')}.csv"
        
        query = {
            "size": 0,
            "aggs": {
                "by_topic": {
                    "terms": {"field": "topic.keyword", "size": 20},
                    "aggs": {
                        "avg_confidence": {"avg": {"field": "confidence"}},
                        "avg_likes": {"avg": {"field": "like_count"}},
                        "avg_retweets": {"avg": {"field": "retweet_count"}},
                        "by_sentiment": {
                            "terms": {"field": "sentiment.keyword"}
                        }
                    }
                }
            }
        }
        
        result = self.es.search(index=self.index, body=query)
        buckets = result['aggregations']['by_topic']['buckets']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Topic', 'Total Tweets', 'Confiance Moy.', 'Likes Moy.', 'RT Moy.',
                'Positifs', 'Neutres', 'Négatifs'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for bucket in buckets:
                sentiments = {
                    b['key']: b['doc_count'] 
                    for b in bucket['by_sentiment']['buckets']
                }
                
                row = {
                    'Topic': bucket['key'],
                    'Total Tweets': bucket['doc_count'],
                    'Confiance Moy.': f"{bucket['avg_confidence']['value']:.2f}",
                    'Likes Moy.': f"{bucket['avg_likes']['value']:.1f}",
                    'RT Moy.': f"{bucket['avg_retweets']['value']:.1f}",
                    'Positifs': sentiments.get('positive', 0),
                    'Neutres': sentiments.get('neutral', 0),
                    'Négatifs': sentiments.get('negative', 0)
                }
                
                writer.writerow(row)
        
        print(f"✅ Export stats par topic : {filename}")
        
        return filename


if __name__ == "__main__":
    exporter = ElasticsearchCSVExporter()
    
    # Export complet
    print("📥 Export 1 : Tous les tweets")
    exporter.export_all_tweets()
    
    # Export par sentiment
    print("\n📥 Export 2 : Tweets positifs")
    exporter.export_by_sentiment('positive')
    
    print("\n📥 Export 3 : Tweets négatifs")
    exporter.export_by_sentiment('negative')
    
    # Top hashtags
    print("\n📥 Export 4 : Top hashtags")
    exporter.export_top_hashtags()
    
    # Stats par topic
    print("\n📥 Export 5 : Stats par topic")
    exporter.export_stats_by_topic()
    
    print("\n✅ Tous les exports terminés !")
#!/usr/bin/env python3
"""
Export en JSON pour intégration API
"""

from elasticsearch import Elasticsearch
import json
from datetime import datetime

class JSONExporter:
    def __init__(self):
        self.es = Elasticsearch(["http://localhost:9200"])
    
    def export_to_json(self, filename=None, max_size=1000):
        """Exporte en JSON"""
        if filename is None:
            filename = f"tweets_{datetime.now().strftime('%Y%m%d')}.json"
        
        result = self.es.search(
            index="tweets_index_improved",
            body={"query": {"match_all": {}}, "size": max_size}
        )
        
        tweets = [hit['_source'] for hit in result['hits']['hits']]
        
        # Sauvegarder
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tweets, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON créé : {filename}")
        print(f"📊 {len(tweets)} tweets exportés")
        
        return filename


if __name__ == "__main__":
    exporter = JSONExporter()
    exporter.export_to_json()
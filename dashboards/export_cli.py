#!/usr/bin/env python3
"""
Interface CLI pour tous les exports
"""

import argparse
from export_es_to_csv import ElasticsearchCSVExporter
from export_cassandra_to_csv import CassandraCSVExporter
from export_to_excel import ExcelExporter
from export_to_json import JSONExporter

def main():
    parser = argparse.ArgumentParser(description='Exporter les données Twitter')
    
    parser.add_argument(
        '--format',
        choices=['csv', 'excel', 'json', 'all'],
        default='csv',
        help='Format d\'export (défaut: csv)'
    )
    
    parser.add_argument(
        '--source',
        choices=['elasticsearch', 'cassandra', 'both'],
        default='elasticsearch',
        help='Source des données (défaut: elasticsearch)'
    )
    
    parser.add_argument(
        '--filter',
        choices=['all', 'positive', 'negative', 'neutral'],
        default='all',
        help='Filtrer par sentiment (défaut: all)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Nom du fichier de sortie'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("📤 EXPORT TWITTER ANALYTICS")
    print("=" * 80)
    print(f"Format  : {args.format}")
    print(f"Source  : {args.source}")
    print(f"Filtre  : {args.filter}")
    print("=" * 80)
    print()
    
    # Elasticsearch
    if args.source in ['elasticsearch', 'both']:
        es_exporter = ElasticsearchCSVExporter()
        
        if args.format == 'csv' or args.format == 'all':
            if args.filter == 'all':
                es_exporter.export_all_tweets(args.output)
            else:
                es_exporter.export_by_sentiment(args.filter, args.output)
        
        if args.format == 'excel' or args.format == 'all':
            excel_exporter = ExcelExporter()
            excel_exporter.export_to_excel(args.output)
        
        if args.format == 'json' or args.format == 'all':
            json_exporter = JSONExporter()
            json_exporter.export_to_json(args.output)
    
    # Cassandra
    if args.source in ['cassandra', 'both']:
        cassandra_exporter = CassandraCSVExporter()
        cassandra_exporter.export_all_tweets(args.output)
    
    print()
    print("✅ Exports terminés !")


if __name__ == "__main__":
    main()
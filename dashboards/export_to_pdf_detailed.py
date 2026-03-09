#!/usr/bin/env python3
"""
Export PDF détaillé avec graphiques
"""

from elasticsearch import Elasticsearch
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime

class DetailedPDFExporter:
    def __init__(self):
        self.es = Elasticsearch(["http://localhost:9200"])
    
    def export_detailed_pdf(self, filename=None):
        """Créer un PDF détaillé"""
        if filename is None:
            filename = f"analyse_detaillee_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Titre
        title = Paragraph(
            f"<b>Analyse Détaillée des Tweets</b><br/>{datetime.now().strftime('%d/%m/%Y')}",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Section 1 : Stats globales
        story.append(Paragraph("<b>1. Statistiques Globales</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        total_result = self.es.count(index="tweets_index_improved")
        total = total_result['count']
        
        stats_data = [
            ['Métrique', 'Valeur'],
            ['Total de tweets', str(total)],
            ['Période', datetime.now().strftime('%d/%m/%Y')],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Section 2 : Top tweets
        story.append(Paragraph("<b>2. Top 10 Tweets (par engagement)</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Query top tweets
        top_query = {
            "query": {"match_all": {}},
            "sort": [{"like_count": "desc"}],
            "size": 10
        }
        
        top_result = self.es.search(index="tweets_index_improved", body=top_query)
        
        tweets_data = [['#', 'User', 'Texte (extrait)', 'Likes', 'RT']]
        
        for i, hit in enumerate(top_result['hits']['hits'], 1):
            tweet = hit['_source']
            text = tweet.get('text', '')[:50] + '...'
            tweets_data.append([
                str(i),
                tweet.get('user', ''),
                text,
                str(tweet.get('like_count', 0)),
                str(tweet.get('retweet_count', 0))
            ])
        
        tweets_table = Table(tweets_data, colWidths=[0.4*inch, 1*inch, 3*inch, 0.6*inch, 0.6*inch])
        tweets_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(tweets_table)
        
        # Build PDF
        doc.build(story)
        print(f"✅ PDF détaillé créé : {filename}")
        
        return filename


if __name__ == "__main__":
    exporter = DetailedPDFExporter()
    exporter.export_detailed_pdf()